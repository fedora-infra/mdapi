package lookup

import (
	"database/sql"
	"fmt"
	_ "github.com/mattn/go-sqlite3"
	"metasource/metasource/config"
	"metasource/metasource/models/home"
	"os"
)

var ReadPrmy = func(vers *string, name *string) (home.PackUnit, string, error) {
	var base *sql.DB
	var rows *sql.Rows
	var stmt *sql.Stmt
	var expt error
	var item, path, sqlq string
	var exst bool
	var rslt home.PackUnit

	list := []string{"updates-testing", "updates", "testing", ""}

	for _, item = range list {
		switch item {
		case "updates-testing", "updates", "testing":
			path = fmt.Sprintf("%s/%s", config.DBFOLDER, fmt.Sprintf("metasource-%s-%s-primary.sqlite", *vers, item))
		default:
			path = fmt.Sprintf("%s/%s", config.DBFOLDER, fmt.Sprintf("metasource-%s-primary.sqlite", *vers))
		}
		_, expt = os.Stat(path)
		if os.IsNotExist(expt) {
			continue
		}
		exst = true
		break
	}

	if !exst {
		return rslt, item, fmt.Errorf("database file does not exist")
	}

	base, expt = sql.Open(config.DBDRIVER, path)
	if expt != nil {
		return rslt, item, expt
	}
	defer base.Close()

	sqlq = fmt.Sprintf(config.OBTAIN_PACKAGE)

	stmt, expt = base.Prepare(sqlq)
	if expt != nil {
		return rslt, item, expt
	}
	defer stmt.Close()

	rows, _ = stmt.Query(*name)
	defer rows.Close()

	if rows.Next() {
		expt = rows.Scan(&rslt.Key, &rslt.Id, &rslt.Name, &rslt.Source, &rslt.Epoch, &rslt.Version, &rslt.Release, &rslt.Arch, &rslt.Summary, &rslt.Desc, &rslt.Link)
		if expt != nil {
			return rslt, item, expt
		}
	}

	if !rslt.Id.Valid {
		return rslt, item, fmt.Errorf("no result found")
	}

	return rslt, item, nil
}
