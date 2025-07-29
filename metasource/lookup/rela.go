package lookup

import (
	"database/sql"
	"fmt"
	_ "github.com/mattn/go-sqlite3"
	"metasource/metasource/config"
	"metasource/metasource/models/home"
	"os"
)

var ReadRelation = func(vers *string, pack *home.PackUnit, repo *string, relation *string) ([]home.PackUnit, error) {
	var base *sql.DB
	var rows *sql.Rows
	var stmt *sql.Stmt
	var expt error
	var path, sqlq string
	var rslt []home.PackUnit
	var pkit home.PackUnit

	switch *repo {
	case "updates-testing", "updates", "testing":
		path = fmt.Sprintf("%s/%s", config.DBFOLDER, fmt.Sprintf("metasource-%s-%s-primary.sqlite", *vers, *repo))
	default:
		path = fmt.Sprintf("%s/%s", config.DBFOLDER, fmt.Sprintf("metasource-%s-primary.sqlite", *vers))
	}
	_, expt = os.Stat(path)
	if os.IsNotExist(expt) {
		return rslt, expt
	}

	base, expt = sql.Open(config.DBDRIVER, path)
	if expt != nil {
		return rslt, expt
	}
	defer base.Close()

	sqlq = fmt.Sprintf(config.OBTAIN_PACKAGE_BY, *relation)

	stmt, expt = base.Prepare(sqlq)
	if expt != nil {
		return rslt, expt
	}
	defer stmt.Close()

	rows, _ = stmt.Query(pack.Name)
	defer rows.Close()

	rslt = []home.PackUnit{}

	for rows.Next() {
		expt = rows.Scan(&pkit.Key, &pkit.Id, &pkit.Name, &pkit.Source, &pkit.Epoch, &pkit.Version, &pkit.Release, &pkit.Arch, &pkit.Summary, &pkit.Desc, &pkit.Link)
		if expt != nil {
			return rslt, expt
		}
		rslt = append(rslt, pkit)
	}

	return rslt, expt
}
