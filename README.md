# Intelbras Solar Home Assistant Integration

Home Assistant integration for the [Intelbras Solar monitoring portal](http://solar-monitoramento.intelbras.com.br/).

## Requirements

**Home Assistant 2026.9.0 or newer.** HACS enforces this and will not offer the
integration on an older install. If you are behind, upgrade Home Assistant first
— including from a YAML configuration of this integration, see
[Upgrading from YAML](#upgrading-from-yaml).

## Installation

1. In HACS, open the three-dot menu → **Custom repositories**.
2. Add `https://github.com/magic7s/intelbras-solar` with type **Integration**.
3. Find **Intelbras Solar** in HACS and select **Download**.
4. Restart Home Assistant.

To install without HACS, copy `custom_components/intelbras_solar/` into your
`config/custom_components/` directory and restart.

## Configuration

Go to **Settings → Devices & Services → Add Integration**, search for
**Intelbras Solar**, and sign in with the account you use on the portal. The
credentials are checked against the portal before the entry is created.

One entry per portal account; adding the same username twice is rejected. If the
password stops working later, Home Assistant raises a repair notification and
prompts you to re-enter it — the integration is not removed and its history is
kept.

## Upgrading from YAML

The YAML configuration is deprecated. It is still imported automatically on the
first start after upgrading, and a repair notification then tells you to delete
the block:

```yaml
# no longer needed
intelbras_solar:
  username: !secret intelbras_username
  password: !secret intelbras_password
```

Because this version requires Home Assistant 2026.9.0, upgrade Home Assistant
**before** updating the integration. Your existing YAML keeps working on the
version you already have until you do.

## What you get

Every plant on the account becomes a device, and every inverter becomes a device
linked to its plant:

| Device   | Entity          | Unit | Notes                                        |
| -------- | --------------- | ---- | -------------------------------------------- |
| Plant    | Total energy    | kWh  | `eTotal` of the whole plant                  |
| Inverter | Instant power   | W    | `pac`                                        |
| Inverter | Energy today    | kWh  | `eToday`, resets at midnight                 |
| Inverter | Energy this month | kWh | `eMonth`                                    |
| Inverter | Total energy    | kWh  | `eTotal` of that inverter                    |
| Inverter | Last reported   | —    | when the portal last heard from the inverter |
| Inverter | Connection      | —    | off once the portal loses the inverter       |

The plant and instant power sensors keep the unique IDs they had before, so
entity IDs, history and anything referencing them survive the upgrade.

The portal only refreshes inverter data every few minutes, so the integration
polls every 5 minutes.

## About the portal connection

The Intelbras portal does not serve HTTPS — it refuses connections on port 443 —
so the integration talks to it over plain HTTP, and your portal username and
password are sent unencrypted on every poll. Nothing in this integration can
change that. Use a password you do not reuse anywhere else.

## Brand images

`brand/` carries the icon and logo Home Assistant shows for the integration.
Since 2026.3 a custom integration serves these itself and they take priority
over the brands CDN, which no longer accepts custom integration submissions.
