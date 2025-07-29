package lookup

import (
	"database/sql"
	"fmt"
	_ "github.com/mattn/go-sqlite3"
	"metasource/metasource/config"
	"metasource/metasource/models/home"
	"os"
)

var ReadOthr = func(vers *string, pack *home.PackUnit, repo *string) (home.OthrRslt, error) {
	var base *sql.DB
	var rows *sql.Rows
	var stmt *sql.Stmt
	var expt error
	var path, sqlq string
	var lgit home.OthrUnit

	rslt := home.OthrRslt{List: []home.OthrUnit{}}

	switch *repo {
	case "updates-testing", "updates", "testing":
		path = fmt.Sprintf("%s/%s", config.DBFOLDER, fmt.Sprintf("metasource-%s-%s-other.sqlite", *vers, *repo))
	default:
		path = fmt.Sprintf("%s/%s", config.DBFOLDER, fmt.Sprintf("metasource-%s-other.sqlite", *vers))
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

	sqlq = fmt.Sprintf(config.OBTAIN_CHANGELOGS)

	stmt, expt = base.Prepare(sqlq)
	if expt != nil {
		return rslt, expt
	}
	defer stmt.Close()

	rows, _ = stmt.Query(pack.Id)
	defer rows.Close()

	for rows.Next() {
		expt = rows.Scan(&lgit.Key, &lgit.Author, &lgit.Text, &lgit.Date)
		if expt != nil {
			return rslt, expt
		}
		rslt.List = append(rslt.List, lgit)
	}

	return rslt, expt
}
