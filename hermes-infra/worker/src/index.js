/**
 * Hermes License Validation Proxy
 * Cloudflare Worker — validates Hermes license keys via the Whop API.
 *
 * Environment variables (set via `wrangler secret put`):
 *   WHOP_API_KEY  — Bearer token for the Whop API
 */

// ---------------------------------------------------------------------------
// Constants
// ---------------------------------------------------------------------------

const LICENSE_REGEX = /^HERMES-[A-Z0-9]{4}-[A-Z0-9]{4}-[A-Z0-9]{4}$/;

const CORS_HEADERS = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Methods": "POST, OPTIONS",
  "Access-Control-Allow-Headers": "Content-Type, Authorization",
  "Access-Control-Max-Age": "86400",
};

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

/**
 * Build a JSON response with CORS headers attached.
 *
 * @param {unknown} body      — value that will be JSON-serialised
 * @param {number}  status    — HTTP status code (default 200)
 * @returns {Response}
 */
function jsonResponse(body, status = 200) {
  return new Response(JSON.stringify(body), {
    status,
    headers: {
      "Content-Type": "application/json;charset=UTF-8",
      ...CORS_HEADERS,
    },
  });
}

/**
 * Build a standardised error response.
 *
 * @param {string} error   — human-readable error description
 * @param {number} status  — HTTP status code
 * @returns {Response}
 */
function errorResponse(error, status = 400) {
  return jsonResponse({ valid: false, error }, status);
}

// ---------------------------------------------------------------------------
// Whop API call
// ---------------------------------------------------------------------------

/**
 * Call the Whop membership-validate endpoint and return the parsed payload.
 *
 * @param {string} licenseKey — the raw license key (used as the membership ID)
 * @param {string} whopApiKey — the Whop API bearer token
 * @returns {Promise<{ ok: boolean, data?: object, error?: string }>}
 */
async function fetchWhopValidation(licenseKey, whopApiKey) {
  const url = `https://api.whop.com/api/v2/memberships/${encodeURIComponent(licenseKey)}/validate`;

  let response;
  try {
    response = await fetch(url, {
      method: "GET",
      headers: {
        Authorization: `Bearer ${whopApiKey}`,
        "Content-Type": "application/json",
      },
    });
  } catch (err) {
    return { ok: false, error: `Network error reaching Whop API: ${err.message}` };
  }

  // Whop returns 200 for valid memberships; 404 / 422 for invalid / not found
  if (response.status === 404) {
    return { ok: false, error: "License key not found" };
  }

  let json;
  try {
    json = await response.json();
  } catch {
    return { ok: false, error: "Invalid response from Whop API" };
  }

  if (!response.ok) {
    // Whop error body usually has { error: { message: "..." } }
    const msg =
      json?.error?.message ||
      json?.message ||
      `Whop API returned status ${response.status}`;
    return { ok: false, error: msg };
  }

  return { ok: true, data: json };
}

// ---------------------------------------------------------------------------
// Response mapper
// ---------------------------------------------------------------------------

/**
 * Map the raw Whop membership object to the clean Hermes validation shape.
 *
 * Whop membership fields of interest:
 *   id, status, plan.name, user.email, renewal_period_end (Unix seconds)
 *
 * @param {object} whopData — the JSON body returned by Whop
 * @returns {object}
 */
function mapWhopResponse(whopData) {
  // A membership is valid when its status is "active" or "trialing"
  const validStatuses = new Set(["active", "trialing"]);
  const isValid = validStatuses.has(whopData?.status);

  // Derive tier from the plan name (lowercase, default "pro")
  const planName = whopData?.plan?.name ?? "";
  const tier = planName.toLowerCase() || "pro";

  // Email from the nested user object
  const email = whopData?.user?.email ?? null;

  // Expiry: Whop stores `renewal_period_end` as a Unix timestamp (seconds)
  let expiresAt = null;
  if (whopData?.renewal_period_end) {
    expiresAt = new Date(whopData.renewal_period_end * 1000).toISOString();
  }

  return {
    valid: isValid,
    tier,
    email,
    expires_at: expiresAt,
    membership_id: whopData?.id ?? null,
  };
}

// ---------------------------------------------------------------------------
// Request handler
// ---------------------------------------------------------------------------

/**
 * Handle POST /v1/validate
 *
 * Expected body: { "license_key": "HERMES-XXXX-XXXX-XXXX", "device_id": "..." }
 *
 * @param {Request} request
 * @param {object}  env      — Worker env bindings
 * @returns {Promise<Response>}
 */
async function handleValidate(request, env) {
  // --- Parse request body ---------------------------------------------------
  let body;
  try {
    body = await request.json();
  } catch {
    return errorResponse("Request body must be valid JSON", 400);
  }

  const { license_key, device_id } = body ?? {};

  if (!license_key || typeof license_key !== "string") {
    return errorResponse("Missing required field: license_key", 400);
  }

  if (!device_id || typeof device_id !== "string") {
    return errorResponse("Missing required field: device_id", 400);
  }

  // --- Validate format ------------------------------------------------------
  const normalised = license_key.trim().toUpperCase();

  if (!LICENSE_REGEX.test(normalised)) {
    return errorResponse(
      "Invalid license key format. Expected: HERMES-XXXX-XXXX-XXXX",
      400
    );
  }

  // --- Check env configuration ----------------------------------------------
  if (!env.WHOP_API_KEY) {
    console.error("WHOP_API_KEY environment variable is not configured");
    return errorResponse("Server configuration error", 500);
  }

  // --- Call Whop API --------------------------------------------------------
  const { ok, data, error } = await fetchWhopValidation(
    normalised,
    env.WHOP_API_KEY
  );

  if (!ok) {
    // Distinguish between a "license not found" (200 valid:false) and a
    // genuine upstream/server error (502)
    const isServerError =
      error &&
      (error.startsWith("Network error") ||
        error.startsWith("Invalid response") ||
        error.startsWith("Server"));

    return jsonResponse(
      { valid: false, error },
      isServerError ? 502 : 200
    );
  }

  // --- Map and return -------------------------------------------------------
  const result = mapWhopResponse(data);
  return jsonResponse(result, 200);
}

// ---------------------------------------------------------------------------
// Main entry point
// ---------------------------------------------------------------------------

export default {
  /**
   * @param {Request} request
   * @param {object}  env
   * @param {object}  ctx
   * @returns {Promise<Response>}
   */
  async fetch(request, env, ctx) {
    const url = new URL(request.url);
    const method = request.method.toUpperCase();

    // ------------------------------------------------------------------
    // CORS preflight
    // ------------------------------------------------------------------
    if (method === "OPTIONS") {
      return new Response(null, {
        status: 204,
        headers: CORS_HEADERS,
      });
    }

    // ------------------------------------------------------------------
    // Route: POST /v1/validate
    // ------------------------------------------------------------------
    if (method === "POST" && url.pathname === "/v1/validate") {
      return handleValidate(request, env);
    }

    // ------------------------------------------------------------------
    // Health check: GET /health  (useful for uptime monitoring)
    // ------------------------------------------------------------------
    if (method === "GET" && url.pathname === "/health") {
      return jsonResponse({ status: "ok", service: "hermes-license-proxy" });
    }

    // ------------------------------------------------------------------
    // 404 fallback
    // ------------------------------------------------------------------
    return errorResponse("Not found", 404);
  },
};
