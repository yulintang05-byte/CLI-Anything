#!/usr/bin/env bash
# ==============================================================================
#  Hermes — Installer
#  https://whop.com/hermes
#
#  Usage:
#    curl -fsSL https://raw.githubusercontent.com/YOUR_USERNAME/hermes/main/install.sh | bash
#    -- or --
#    bash install.sh
#
#  Environment overrides:
#    HERMES_VERSION   — pin a specific release, e.g. HERMES_VERSION=1.2.0
#    HERMES_INSTALL   — override install directory (default: $HOME/.local/bin)
# ==============================================================================

set -euo pipefail

# ------------------------------------------------------------------------------
# Colour helpers (disabled when not a TTY)
# ------------------------------------------------------------------------------
if [ -t 1 ] && command -v tput &>/dev/null && tput colors &>/dev/null && [ "$(tput colors)" -ge 8 ]; then
  BOLD="$(tput bold)"
  RED="$(tput setaf 1)"
  GREEN="$(tput setaf 2)"
  YELLOW="$(tput setaf 3)"
  CYAN="$(tput setaf 6)"
  WHITE="$(tput setaf 7)"
  RESET="$(tput sgr0)"
else
  BOLD="" RED="" GREEN="" YELLOW="" CYAN="" WHITE="" RESET=""
fi

# ------------------------------------------------------------------------------
# Logging
# ------------------------------------------------------------------------------
info()    { printf "%s  %s%s\n"    "${CYAN}›${RESET}"  "$*"              "${RESET}"; }
success() { printf "%s  %s%s\n"    "${GREEN}✔${RESET}" "${GREEN}$*"      "${RESET}"; }
warn()    { printf "%s  %s%s\n"    "${YELLOW}!${RESET}" "${YELLOW}$*"    "${RESET}"; }
die()     { printf "%s  %s%s\n"    "${RED}✘${RESET}"   "${RED}$*"        "${RESET}" >&2; exit 1; }

# ------------------------------------------------------------------------------
# Dependency checks
# ------------------------------------------------------------------------------
need_cmd() {
  if ! command -v "$1" &>/dev/null; then
    die "Required command not found: '$1'. Please install it and re-run this script."
  fi
}

need_cmd curl

# tar is only needed if we ever ship .tar.gz archives — single-binary for now,
# but let's warn gracefully rather than die hard.
if ! command -v tar &>/dev/null; then
  warn "'tar' not found — will attempt raw binary download only."
fi

# ------------------------------------------------------------------------------
# Detect OS and architecture
# ------------------------------------------------------------------------------
detect_platform() {
  local os arch

  case "$(uname -s)" in
    Linux*)  os="linux"  ;;
    Darwin*) os="darwin" ;;
    *)       die "Unsupported operating system: $(uname -s). Hermes supports Linux and macOS." ;;
  esac

  case "$(uname -m)" in
    x86_64 | amd64)         arch="x86_64"  ;;
    aarch64 | arm64)        arch="aarch64" ;;
    *)                      die "Unsupported architecture: $(uname -m). Hermes supports x86_64 and aarch64." ;;
  esac

  echo "${os}-${arch}"
}

# ------------------------------------------------------------------------------
# Resolve version — GitHub latest release or hardcoded fallback
# ------------------------------------------------------------------------------
resolve_version() {
  if [ -n "${HERMES_VERSION:-}" ]; then
    echo "${HERMES_VERSION}"
    return
  fi

  local api_url="https://api.github.com/repos/YOUR_USERNAME/hermes/releases/latest"
  local version

  version=$(
    curl --silent --fail --location \
      --max-time 10 \
      --header "Accept: application/vnd.github+json" \
      "${api_url}" 2>/dev/null \
    | grep '"tag_name"' \
    | head -1 \
    | sed 's/.*"tag_name": *"v\?\([^"]*\)".*/\1/'
  ) || true

  if [ -z "${version}" ]; then
    warn "Could not fetch latest version from GitHub. Falling back to 1.0.0."
    version="1.0.0"
  fi

  echo "${version}"
}

# ------------------------------------------------------------------------------
# Download helpers
# ------------------------------------------------------------------------------
download() {
  local url="$1"
  local dest="$2"

  curl \
    --silent \
    --show-error \
    --fail \
    --location \
    --progress-bar \
    --output "${dest}" \
    "${url}"
}

# Try to download and verify a SHA256 checksum file.
# Returns 0 if the checksum file was found and verification passed.
# Returns 1 if the checksum file was not found (not fatal — skip verification).
# Calls die() if the checksum file was found but verification failed.
verify_checksum() {
  local binary_path="$1"
  local checksum_url="$2"
  local tmp_sum
  tmp_sum="$(mktemp)"

  info "Fetching checksum file…"

  local http_code
  http_code=$(
    curl --silent --output "${tmp_sum}" \
         --write-out "%{http_code}" \
         --location --max-time 10 \
         "${checksum_url}" 2>/dev/null
  ) || http_code="000"

  if [ "${http_code}" -eq 404 ] || [ ! -s "${tmp_sum}" ]; then
    warn "No checksum file found at release — skipping verification."
    rm -f "${tmp_sum}"
    return 1
  fi

  info "Verifying SHA256 checksum…"

  local binary_name
  binary_name="$(basename "${binary_path}")"

  # The checksum file can be in either "<hash>  <filename>" or
  # "<hash> *<filename>" format. We grep for the binary name and
  # verify against the computed hash.
  local expected_hash
  expected_hash=$(grep -F "${binary_name}" "${tmp_sum}" | awk '{print $1}') || true

  if [ -z "${expected_hash}" ]; then
    warn "Binary not listed in checksum file — skipping verification."
    rm -f "${tmp_sum}"
    return 1
  fi

  local actual_hash
  if command -v sha256sum &>/dev/null; then
    actual_hash=$(sha256sum "${binary_path}" | awk '{print $1}')
  elif command -v shasum &>/dev/null; then
    actual_hash=$(shasum -a 256 "${binary_path}" | awk '{print $1}')
  else
    warn "No sha256sum / shasum tool found — skipping checksum verification."
    rm -f "${tmp_sum}"
    return 1
  fi

  rm -f "${tmp_sum}"

  if [ "${actual_hash}" != "${expected_hash}" ]; then
    die "Checksum mismatch!
  Expected: ${expected_hash}
  Got:      ${actual_hash}
Download may be corrupt or tampered with. Aborting."
  fi

  success "Checksum verified."
  return 0
}

# ------------------------------------------------------------------------------
# PATH configuration
# ------------------------------------------------------------------------------
add_to_path() {
  local install_dir="$1"
  local path_line='export PATH="'"${install_dir}"':$PATH"'

  # Candidates to update (in preference order)
  local shell_configs=()

  # Shell-specific rc files
  [ -n "${ZSH_VERSION:-}"  ] && shell_configs+=("${HOME}/.zshrc")
  [ -n "${BASH_VERSION:-}" ] && shell_configs+=("${HOME}/.bashrc")

  # Always try the common ones
  shell_configs+=(
    "${HOME}/.zshrc"
    "${HOME}/.bashrc"
    "${HOME}/.profile"
  )

  # Deduplicate while preserving order (pure bash)
  local seen=()
  local unique_configs=()
  for cfg in "${shell_configs[@]}"; do
    local already=0
    for s in "${seen[@]:-}"; do [ "$s" = "$cfg" ] && already=1 && break; done
    if [ "$already" -eq 0 ]; then
      seen+=("$cfg")
      unique_configs+=("$cfg")
    fi
  done

  local updated_any=0
  for rc in "${unique_configs[@]}"; do
    # Skip files that already contain the install_dir in PATH
    if [ -f "${rc}" ] && grep -qF "${install_dir}" "${rc}" 2>/dev/null; then
      continue
    fi

    # Create the file if it doesn't exist (e.g. fresh .profile)
    {
      printf '\n# Hermes — added by installer\n'
      printf '%s\n' "${path_line}"
    } >> "${rc}" 2>/dev/null || { warn "Could not write to ${rc}"; continue; }

    success "Added ${install_dir} to PATH in ${rc}"
    updated_any=1
  done

  if [ "${updated_any}" -eq 0 ]; then
    info "${install_dir} is already present in your shell config files."
  fi
}

# ------------------------------------------------------------------------------
# Welcome banner (shown after successful install)
# ------------------------------------------------------------------------------
print_welcome() {
  local version="$1"

  printf "\n"
  printf "%s%s╔══════════════════════════════════════════════════════════╗%s\n" "${BOLD}" "${CYAN}" "${RESET}"
  printf "%s%s║                                                          ║%s\n" "${BOLD}" "${CYAN}" "${RESET}"
  printf "%s%s║    ██╗  ██╗███████╗██████╗ ███╗   ███╗███████╗███████╗  ║%s\n" "${BOLD}" "${WHITE}" "${RESET}"
  printf "%s%s║    ██║  ██║██╔════╝██╔══██╗████╗ ████║██╔════╝██╔════╝  ║%s\n" "${BOLD}" "${WHITE}" "${RESET}"
  printf "%s%s║    ███████║█████╗  ██████╔╝██╔████╔██║█████╗  ███████╗  ║%s\n" "${BOLD}" "${WHITE}" "${RESET}"
  printf "%s%s║    ██╔══██║██╔══╝  ██╔══██╗██║╚██╔╝██║██╔══╝  ╚════██║  ║%s\n" "${BOLD}" "${WHITE}" "${RESET}"
  printf "%s%s║    ██║  ██║███████╗██║  ██║██║ ╚═╝ ██║███████╗███████║  ║%s\n" "${BOLD}" "${WHITE}" "${RESET}"
  printf "%s%s║    ╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝╚═╝     ╚═╝╚══════╝╚══════╝  ║%s\n" "${BOLD}" "${WHITE}" "${RESET}"
  printf "%s%s║                                                          ║%s\n" "${BOLD}" "${CYAN}" "${RESET}"
  printf "%s%s║%s    %sThe terminal Claude deserves.%s                         %s%s║%s\n" \
         "${BOLD}" "${CYAN}" "${RESET}" "${YELLOW}" "${RESET}" "${BOLD}" "${CYAN}" "${RESET}"
  printf "%s%s║                                                          ║%s\n" "${BOLD}" "${CYAN}" "${RESET}"
  printf "%s%s╚══════════════════════════════════════════════════════════╝%s\n" "${BOLD}" "${CYAN}" "${RESET}"
  printf "\n"
  printf "  %s%s Installation complete!%s  Hermes %sv%s%s is ready.\n" \
         "${BOLD}" "${GREEN}" "${RESET}" "${CYAN}" "${version}" "${RESET}"
  printf "\n"
  printf "  %s Get a license key:%s\n" "${BOLD}" "${RESET}"
  printf "    %shttps://whop.com/hermes%s\n" "${CYAN}" "${RESET}"
  printf "\n"
  printf "  %s Start Hermes:%s\n" "${BOLD}" "${RESET}"
  printf "    %shermes%s\n" "${GREEN}" "${RESET}"
  printf "\n"
  printf "  %sNote:%s Restart your terminal (or run %ssource ~/.bashrc%s) to\n" \
         "${YELLOW}" "${RESET}" "${CYAN}" "${RESET}"
  printf "  ensure %s\$HOME/.local/bin%s is on your PATH.\n" "${CYAN}" "${RESET}"
  printf "\n"
}

# ------------------------------------------------------------------------------
# Main
# ------------------------------------------------------------------------------
main() {
  printf "\n%s%s Hermes Installer%s\n\n" "${BOLD}" "${CYAN}" "${RESET}"

  # 1. Detect platform
  info "Detecting platform…"
  local platform
  platform="$(detect_platform)"
  success "Platform: ${platform}"

  # 2. Resolve version
  info "Resolving version…"
  local version
  version="$(resolve_version)"
  success "Version: ${version}"

  # 3. Build URLs
  local base_url="https://github.com/YOUR_USERNAME/hermes/releases/download/v${version}"
  local binary_name="hermes-${platform}"
  local binary_url="${base_url}/${binary_name}"
  local checksum_url="${base_url}/checksums.txt"

  # 4. Determine install directory
  local install_dir="${HERMES_INSTALL:-${HOME}/.local/bin}"
  local install_path="${install_dir}/hermes"

  info "Install directory: ${install_dir}"

  # Create install directory if it doesn't exist
  if [ ! -d "${install_dir}" ]; then
    mkdir -p "${install_dir}" || die "Failed to create install directory: ${install_dir}"
    success "Created ${install_dir}"
  fi

  # 5. Download binary to a temporary file
  local tmp_binary
  tmp_binary="$(mktemp)"
  # Ensure we clean up the temp file on any exit
  trap 'rm -f "${tmp_binary}"' EXIT

  info "Downloading ${binary_name} from GitHub…"
  if ! download "${binary_url}" "${tmp_binary}"; then
    die "Download failed. Check your internet connection or visit:
  ${base_url}"
  fi
  success "Download complete."

  # 6. Verify checksum (optional — skips gracefully if no checksum file)
  verify_checksum "${tmp_binary}" "${checksum_url}" || true

  # 7. Install
  info "Installing to ${install_path}…"
  chmod +x "${tmp_binary}"
  mv -f "${tmp_binary}" "${install_path}" || die "Failed to install binary to ${install_path}"
  # Trap no longer needs to clean up (file was moved)
  trap - EXIT
  success "Installed hermes to ${install_path}"

  # 8. Add to PATH
  add_to_path "${install_dir}"

  # 9. Quick sanity check
  if "${install_path}" --version &>/dev/null; then
    local installed_version
    installed_version=$("${install_path}" --version 2>&1 | head -1)
    info "Binary reports: ${installed_version}"
  fi

  # 10. Welcome banner
  print_welcome "${version}"
}

main "$@"
