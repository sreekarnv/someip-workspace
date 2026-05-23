#!/bin/bash
set -e

PROCESS_TYPE=${PROCESS_TYPE:-service}
EXAMPLE_NAME=${EXAMPLE_NAME:-DoorControl}

snake_name=$(echo "$EXAMPLE_NAME" | sed -r 's/([A-Z])/_\1/g' | tr '[:upper:]' '[:lower:]' | sed 's/^_//')

resolve_ip() {
    local host="$1"

    if [ -z "$host" ]; then
        return 1
    fi

    if [[ "$host" =~ ^[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
        printf '%s\n' "$host"
        return 0
    fi

    getent ahostsv4 "$host" | awk 'NR == 1 { print $1; exit }'
}

prepare_vsomeip_config() {
    local source_config="${VSOMEIP_CONFIGURATION:-/app/vsomeip.json}"
    local own_host own_ip remote_host remote_ip runtime_config

    if [ ! -f "$source_config" ]; then
        return
    fi

    own_host=$(jq -r '.unicast // empty' "$source_config")
    own_ip=$(resolve_ip "$own_host" || true)
    remote_host=$(jq -r '.services[]?.unicast // empty' "$source_config" | head -n 1)
    remote_ip=$(resolve_ip "$remote_host" || true)

    if [ -z "$own_ip" ]; then
        echo "Unable to resolve vsomeip unicast host: $own_host" >&2
        exit 1
    fi

    sd_multicast=$(jq -r '."service-discovery".multicast // empty' "$source_config")
    if [ -n "$sd_multicast" ] && command -v ip >/dev/null 2>&1; then
        ip route replace "$sd_multicast"/32 dev "${VSOMEIP_DEVICE:-eth0}"
    fi

    runtime_config=/tmp/vsomeip.json
    jq --arg own "$own_ip" --arg remote "$remote_ip" \
        '.unicast = $own
         | if $remote == "" then .
           else .services |= map(if has("unicast") then .unicast = $remote else . end)
           end' \
        "$source_config" > "$runtime_config"
    export VSOMEIP_CONFIGURATION="$runtime_config"
}

prepare_vsomeip_config

service_binary=${SERVICE_BINARY:-${snake_name}_service}
client_binary=${CLIENT_BINARY:-${snake_name}_client}

if [ "$PROCESS_TYPE" = "service" ]; then
    exec /app/${service_binary}
elif [ "$PROCESS_TYPE" = "client" ]; then
    if [ "${PROCESS_START_DELAY:-0}" != "0" ]; then
        echo "Delaying client start by ${PROCESS_START_DELAY}s for capture setup..."
        sleep "$PROCESS_START_DELAY"
    fi
    exec /app/${client_binary}
else
    echo "Unknown PROCESS_TYPE: $PROCESS_TYPE"
    exit 1
fi
