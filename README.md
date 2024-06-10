# updateAll
The Universal Package Manager Update Utility

updateAll is currently still in its early stages. It is currently not recommended for regular use.

<!--HELP GEN START-->
## Documentation
| Operation | Usage | Positional Arguments | Options |
| --- | --- | --- | --- |
| **Main** | `updateAll` [`-h`] [`-H`] [`-v`] [`--debug [DEBUG]`] {`update`,`up`,`count`,`ct`,`check-broken`,`ck`} | {`update`,`up`,`count`,`ct`,`check-broken`,`ck`}<br> Operation to perform<br> `update` (`up`)         Update packages<br> `count` (`ct`)          Count upgradable packages<br> `check-broken` (`ck`)   Check for broken packages where supported<br> <br>  | `-h`, `--help`            show this help message and exit<br> `-H`, `--full-help`       Display full updateAll help<br> `-v`, `--version`         show program's version number and exit<br>  |
| **update** | `updateAll update` [`-h`] [`-c`] [`-p`] [`-S`] [`-s SKIP `[`SKIP` ...] [`-V`] [`package_managers` ...] | `package_managers`      Whitelist of package managers to use<br> <br>  | `-h`, `--help`            show this help message and exit<br> `-c`, `--check-broken`    Check for broken packages after updating where<br> supported<br> `-p`, `--simple`          Don't use Live Table output for Package Manager Status<br> `-S`, `--simulate`        Dry run/simulate update process<br> `-s SKIP `[`SKIP` ...], `--skip SKIP `[`SKIP` ...]<br> Skip specified package managers<br> `-V`, `--verbose`         Enable verbose output<br>  |
| **count** | `updateAll count` [`-h`] [`-p`] [`-s SKIP `[`SKIP` ...] [`-V`] [`package_managers` ...] | `package_managers`      Whitelist of package managers to use<br> <br>  | `-h`, `--help`            show this help message and exit<br> `-p`, `--simple`          Don't use Live Table output for Package Manager Status<br> `-s SKIP `[`SKIP` ...], `--skip SKIP `[`SKIP` ...]<br> Skip specified package managers<br> `-V`, `--verbose`         Enable verbose output<br>  |
| **check-broken** | `updateAll check-broken` [`-h`] [`-p`] [`-S`] [`-s SKIP `[`SKIP` ...] [`-V`] [`package_managers` ...] | `package_managers`      Whitelist of package managers to use<br> <br>  | `-h`, `--help`            show this help message and exit<br> `-p`, `--simple`          Don't use Live Table output for Package Manager Status<br> `-S`, `--simulate`        Dry run/simulate check process<br> `-s SKIP `[`SKIP` ...], `--skip SKIP `[`SKIP` ...]<br> Skip specified package managers<br> `-V`, `--verbose`         Enable verbose output<br>  |
<!--HELP GEN END-->

### Known Issues

 - Simple View Live Table does not scroll with progress. Appears to hang during long processes. Does update the screen after step completion.
 - Many modules are currently incomplete.