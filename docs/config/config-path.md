# Path to package
Тут описываются разные варианты указания `path` в config-файле

## Поддержка wildcard
Для того, чтобы задать любой путь, можно использовать `*`. Это пригодится, когда вам нужно выкачать пакеты, в оригинале не обращающие внимания на пути (`nupkg`, `deb`)

```yaml
# deb
parsers:
  common:
    columns:
      version: '{int}.{int}.{int}[.{int}]'
  artifactory-deb:
    path: '{server}/{repo}/pool/*/{package}.{version}.deb'

# nupkg
parsers:
  common:
    columns:
      version: '{int}.{int}.{int}[.{int}][-{str}]'
  artifactory-nupkg:
    path: '{server}/{repo}/pool/*/{package}.{version}.nupkg'
```