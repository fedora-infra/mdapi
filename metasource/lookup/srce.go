package lookup

import (
	"database/sql"
	"errors"
	"fmt"
	_ "github.com/mattn/go-sqlite3"
	"metasource/metasource/config"
	"metasource/metasource/models"
	"os"
	"regexp"
)

var ReadSrce = func(vers *string, name *string) (models.PackUnit, string, error) {
	var base *sql.DB
	var rows *sql.Rows
	var stmt *sql.Stmt
	var expt error
	var item, path, sqlq, escp, ptrn string
	var exst bool
	var pkls []models.PackUnit
	var rslt, pkit models.PackUnit
	var list []string
	var rgxp *regexp.Regexp

	list = []string{"updates-testing", "updates", "testing", ""}

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

		base, expt = sql.Open(config.DBDRIVER, path)
		if expt != nil {
			continue
		}
		defer base.Close()

		sqlq = fmt.Sprintf(config.OBTAIN_PACKAGE_BY_SOURCE)

		stmt, expt = base.Prepare(sqlq)
		if expt != nil {
			return rslt, item, expt
		}
		defer stmt.Close()

		rows, _ = stmt.Query(*name + "-%")
		defer rows.Close()

		for rows.Next() {
			var pack models.PackUnit
			expt = rows.Scan(&pack.Key, &pack.Id, &pack.Name, &pack.Source, &pack.Epoch, &pack.Version, &pack.Release, &pack.Arch, &pack.Summary, &pack.Desc, &pack.Link)
			if expt != nil {
				return rslt, item, expt
			}
			pkls = append(pkls, pack)
		}

		if !rslt.Id.Valid {
			// Try matching with the package name
			for _, pkit = range pkls {
				if pkit.Name.String == *name {
					rslt = pkit
					break
				}
			}
		}

		if !rslt.Id.Valid {
			// Try matching with the pattern of the source RPM name
			escp = regexp.QuoteMeta(*name)
			ptrn = fmt.Sprintf("^%s-[0-9]", escp)
			rgxp = regexp.MustCompile(ptrn)
			for _, pkit = range pkls {
				if rgxp.MatchString(pkit.Source.String) {
					rslt = pkit
					break
				}
			}
		}

		// Attempt next database file if nothing was found here
		// if errors.Is(expt, sql.ErrNoRows) {
		// 	 continue
		// }

		if expt == nil && rslt.Id.Valid {
			break
		}
	}

	if !exst {
		return rslt, item, fmt.Errorf("database files are absent")
	}

	if expt != nil && !errors.Is(expt, sql.ErrNoRows) {
		return rslt, item, expt
	}

	if !rslt.Id.Valid {
		return rslt, item, fmt.Errorf("result absent")
	}

	return rslt, item, expt
}
