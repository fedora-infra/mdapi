package driver

import (
	"database/sql"
	_ "github.com/mattn/go-sqlite3"
	"metasource/metasource/config"
	"metasource/metasource/models/home"
)

func GenerateSignal(unit *home.FileUnit, cast *int) error {
	var base *sql.DB
	var expt error

	base, expt = sql.Open(config.DBDRIVER, unit.Path)
	if expt != nil {
		unit.Keep = false
		return expt
	}
	defer base.Close()

	_, expt = base.Exec(config.SIGNAL_DATABASE)
	if expt != nil {
		unit.Keep = false
		return expt
	}

	unit.Keep = true
	*cast++
	return nil
}
