# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

A Home Assistant custom integration (HACS) for the Intelbras Solar monitoring
portal, a rebranded ShineServer instance.

## Commands

```bash
scripts/setup                       # install runtime + test deps
scripts/lint                        # ruff format . && ruff check . --fix
scripts/develop                     # run Home Assistant with this integration loaded

pytest                              # full suite
pytest tests/test_sensor.py -v      # one module
pytest tests/test_sensor.py::test_name -v
pytest --cov=custom_components.intelbras_solar --cov-report=term-missing

# what CI runs (these must pass; `ruff check --fix` is not enough)
ruff check .
ruff format . --check
mypy custom_components/intelbras_solar
```

## Architecture

One `DataUpdateCoordinator` polls the whole account every 5 minutes and every
entity reads from that single snapshot.

- `intelbras.py` — portal client. Form-POST login sets a session cookie; every
  other endpoint is a POST returning JSON with a `result` flag. Uses **blocking
  `requests`**, so the coordinator calls it via `async_add_executor_job`. Returns
  an `IntelbrasSolarData` snapshot of `Plant` and `Inverter` dataclasses.
- `coordinator.py` — maps client errors onto HA semantics: `IntelbrasSolarAuthError`
  → `ConfigEntryAuthFailed` (triggers reauth), other errors → `UpdateFailed`.
- `entity.py` — `IntelbrasSolarPlantEntity` / `IntelbrasSolarInverterEntity` base
  classes owning the `DeviceInfo`, plus the `available` guards that go false when
  a plant or inverter drops out of the snapshot.
- `sensor.py` / `binary_sensor.py` — entity descriptions with a `value_fn` per
  sensor, so adding a reading is usually one description entry.

**Device hierarchy.** Plants and inverters are separate devices, inverters
parented to their plant. `__init__.py::async_setup_entry` registers the plant
devices _before_ forwarding platforms, because `IntelbrasSolarInverterEntity`
resolves `via_device_id` by looking the plant up in the device registry — that id
does not exist until the plant device is registered. Do not move or drop that
registration loop. (`via_device`, the identifier-tuple form, is deprecated and
removed in HA 2027.8.0.)

**Unique IDs are load-bearing.** Some entities predate the current platform and
carry `legacy_unique_id: bool` on their description to keep the bare plant id or
serial as their unique id. Changing a unique id destroys user history.

## Constraints worth knowing before you change dependencies

**Never pin `pytest`, `pytest-asyncio`, `pytest-cov` or `coverage`.**
`pytest-homeassistant-custom-component` pins all four to exact versions matched to
its target HA release. Declaring any of them independently makes the install
unsatisfiable (`ResolutionImpossible`), not merely inconsistent. PHACC is pinned
exactly in `requirements_test.txt` and is the single source of truth for the test
stack. These four are in `.github/dependabot.yml`'s ignore list for this reason.

**Python 3.14.2+ only.** HA declares `Requires-Python >=3.14.2` and PHACC requires
`>=3.14`; the test stack cannot resolve on anything older. Do not add older
interpreters to the CI matrix — they fail at install, not at test time.

**`homeassistant` is Dependabot-ignored** and must be kept in sync by hand with the
`homeassistant` key in `hacs.json`, which is the minimum version HACS enforces on
users.

**The ruff version is pinned only in `requirements_test.txt`.** `lint.yml` greps it
from there. Don't hardcode a ruff version in a workflow — it silently drifts.

**`.ruff.toml` targets `py314`**, which has two non-obvious effects:

- flake8-type-checking (`TC001`–`TC003`) activates; it is ignored for `tests/**`
  where moving imports into `TYPE_CHECKING` blocks is pure churn.
- the formatter emits PEP 758 unparenthesized `except TypeError, ValueError:`.
  That is valid 3.14+ syntax and `ruff format --check` enforces it — it is not a
  mistake to "fix".

**The portal is HTTP-only.** Port 443 refuses connections and there is no redirect,
so `BASE_URL` cannot be moved to HTTPS. Credentials therefore cross the network in
cleartext on every poll. This is a vendor limitation, not a bug to fix here.

## Deprecations

Home Assistant reports deprecated API use from _custom_ integrations as a logged
`WARNING` (`custom_integration_behavior=LOG`), not an exception — so deprecations
pass tests silently while appearing in every user's log, often with a message
telling them to file a bug report here. When touching HA-facing APIs, check the
captured `WARNING` records rather than trusting a green suite.

## Testing against the live portal

`pytest-homeassistant-custom-component` blocks sockets _and_ patches DNS
resolution session-wide, so a live test needs all three of: restoring
`socket.getaddrinfo` from `pytest_homeassistant_custom_component.plugins`,
`pytest_socket.enable_socket()`, and `socket_allow_hosts([<resolved ip>])` — the
allowlist is IP-based and defaults to `127.0.0.1` only.
