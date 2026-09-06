# Intelbras Solar Home Assistant Integration

Home Assistant integration for the [Intelbras Solar monitoring portal](http://solar-monitoramento.intelbras.com.br/).

## Installation

Add this repository to [HACS](https://hacs.xyz/) as a custom repository, install
**Intelbras Solar**, and restart Home Assistant.

## Configuration

Go to **Settings → Devices & Services → Add Integration**, search for
**Intelbras Solar**, and sign in with the account you use on the portal.

An existing YAML configuration is imported automatically on the first start
after upgrading, so nothing breaks. Once the repair notification shows up, drop
the block from `configuration.yaml`:

```yaml
# no longer needed
intelbras_solar:
  username: !secret intelbras_username
  password: !secret intelbras_password
```

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

The plant and instant power sensors keep the unique IDs they had before, so
entity IDs, history and anything referencing them survive the upgrade.

The portal only refreshes inverter data every few minutes, so the integration
polls every 5 minutes.
