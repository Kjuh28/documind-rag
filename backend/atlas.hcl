data "external_schema" "sqlalchemy" {
  program = [
    "uv",
    "run",
    "python",
    "app/scripts/load_models.py" 
  ]
}

env "local" {
  src = data.external_schema.sqlalchemy.url
  url = "sqlite://vocabulary.db"

  migration {
    dir = "file://migrations"
  }

  dev = "sqlite://file?mode=memory&cache=shared"

  format {
    migrate {
      diff = "{{ sql . \"  \" }}"
    }
  }
}