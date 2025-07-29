package lookup

import (
	"database/sql"
	"fmt"
	_ "github.com/mattn/go-sqlite3"
	"metasource/metasource/config"
	"metasource/metasource/models/home"
	"os"
)

var ReadFile = func(vers *string, pack *home.PackUnit, repo *string) (home.FilelistRslt, error) {
	var base *sql.DB
	var rows *sql.Rows
	var stmt *sql.Stmt
	var expt error
	var path, sqlq string
	var flit home.FilelistUnit

	rslt := home.FilelistRslt{List: []home.FilelistUnit{}}

	switch *repo {
	case "updates-testing", "updates", "testing":
		path = fmt.Sprintf("%s/%s", config.DBFOLDER, fmt.Sprintf("metasource-%s-%s-filelists.sqlite", *vers, *repo))
	default:
		path = fmt.Sprintf("%s/%s", config.DBFOLDER, fmt.Sprintf("metasource-%s-filelists.sqlite", *vers))
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

	sqlq = fmt.Sprintf(config.OBTAIN_FILEUNIT)

	stmt, expt = base.Prepare(sqlq)
	if expt != nil {
		return rslt, expt
	}
	defer stmt.Close()

	rows, _ = stmt.Query(pack.Id)
	defer rows.Close()

	for rows.Next() {
		expt = rows.Scan(&flit.Key, &flit.Directory, &flit.Name, &flit.Type)
		if expt != nil {
			return rslt, expt
		}
		rslt.List = append(rslt.List, flit)
	}

	return rslt, expt
}
