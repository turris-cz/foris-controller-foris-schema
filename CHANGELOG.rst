0.6 (2018-06-19)
----------------

* faster validations (splitted into two - basic an per module)
* schema attribute repalced (base_schema, error_schema, get_module_schema())
* validate_verbose removed (validate() should be verbose enough)
* allow definition overrides in modules (it still fails when override appears in global definitions)
* different error messages `errors` object is place directly in message root instead of inside `data` element
* is_valid function added (check message validity but doesn't raise an exception)

0.5 (2018-05-24)
----------------

* test updates
* mac format checker added
* ipv4prefix, ipv4netmask, ipv6prefix format checkers added

0.4 (2018-02-08)
----------------

* integrate FormatChecker

0.3 (2017-09-25)
----------------

* json definitions can be read from another directory list

0.2 (2017-08-28)
----------------

* json definitions added
* validate_verbose function
* schema validation improvements


0.1 (2017-08-01)
----------------

* initial version
