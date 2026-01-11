package lookup

import (
	"database/sql"
	"errors"
	"fmt"
	_ "github.com/mattn/go-sqlite3"
	"metasource/metasource/config"
	"metasource/metasource/models"
	"os"
)

var ReadPrmy = func(vers *string, name *string) (models.PackUnit, string, error) {
	var base *sql.DB
	var unit *sql.Row
	var expt error
	var item, path string
	var exst bool
	var rslt models.PackUnit

	list := []string{"updates-testing", "updates", "testing", ""}

	for _, item = range list {
		switch item {
		case "updates-testing", "updates", "testing":
			path = fmt.Sprintf(
				"%s/%s",
				config.DBFOLDER,
				fmt.Sprintf("metasource-%s-%s-primary.sqlite", *vers, item),
			)
		default:
			path = fmt.Sprintf(
				"%s/%s",
				config.DBFOLDER,
				fmt.Sprintf("metasource-%s-primary.sqlite", *vers),
			)
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

		unit = base.QueryRow(config.OBTAIN_PACKAGE, name)
		expt = unit.Scan(
			&rslt.Key,
			&rslt.Id,
			&rslt.Name,
			&rslt.Source,
			&rslt.Epoch,
			&rslt.Version,
			&rslt.Release,
			&rslt.Arch,
			&rslt.Summary,
			&rslt.Desc,
			&rslt.Link,
			&rslt.SizePackage,
			&rslt.SizeInstalled,
		)

		if errors.Is(expt, sql.ErrNoRows) {
			continue
		}
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

	return rslt, item, nil
}
