package lookup

import (
	"database/sql"
	"fmt"
	_ "github.com/mattn/go-sqlite3"
	"metasource/metasource/config"
	"metasource/metasource/models"
	"os"
)

var ReadExtn = func(vers *string, pack *models.PackUnit, repo *string) (models.ExtnUnit, error) {
	var base *sql.DB
	var rows *sql.Rows
	var stmt *sql.Stmt
	var expt error
	var item, path, sqlq string
	var dpit models.DepsUnit
	var list []string
	var rslt models.ExtnUnit
	var dpls []models.DepsUnit

	list = []string{
		"supplements",
		"recommends",
		"conflicts",
		"obsoletes",
		"provides",
		"requires",
		"enhances",
		"suggests",
	}

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

	for _, item = range list {
		dpls = []models.DepsUnit{}

		sqlq = fmt.Sprintf(config.OBTAIN_PACKAGE_INFO, item)

		stmt, expt = base.Prepare(sqlq)
		if expt != nil {
			return rslt, expt
		}
		defer stmt.Close()

		rows, _ = stmt.Query(pack.Key)
		defer rows.Close()

		for rows.Next() {
			expt = rows.Scan(&dpit.Id, &dpit.Key, &dpit.Name, &dpit.Epoch, &dpit.Version, &dpit.Release, &dpit.Flags)
			if expt != nil {
				return rslt, expt
			}
			dpls = append(dpls, dpit)
		}

		switch item {
		case "supplements":
			rslt.Supplements = dpls
		case "recommends":
			rslt.Recommends = dpls
		case "conflicts":
			rslt.Conflicts = dpls
		case "obsoletes":
			rslt.Obsoletes = dpls
		case "provides":
			rslt.Provides = dpls
		case "requires":
			rslt.Requires = dpls
		case "enhances":
			rslt.Enhances = dpls
		case "suggests":
			rslt.Suggests = dpls
		}
	}

	rslt.CoPackages, expt = ReadCoop(vers, pack, repo)
	if expt != nil {
		return rslt, expt
	}

	return rslt, expt
}
