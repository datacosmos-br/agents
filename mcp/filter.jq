def active($agent):
  to_entries
  | map(
      select(.key | startswith("_") | not)
      | select((.value.source // "") != "ecc")
      | select((.value | if type == "object" and has("enabled") then .enabled else true end) == true)
      | select((.value.compatibility // []) | index($agent))
      | {
          key: .key,
          value: (
            .value
            | {
                command,
                args: (.args // []),
                type: (.type // "stdio"),
                url,
                headers,
                env: (.env // {}),
                cwd,
                description
              }
            | with_entries(select(.value != null and .value != {}))
          )
        }
    )
  | from_entries;

{($root): active($agent)}
