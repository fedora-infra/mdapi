package driver

import (
	"context"
	"fmt"
	"log/slog"
	"metasource/metasource/config"
	"metasource/metasource/models/home"
	"regexp"
	"strings"
)

var PopulateRepositories = func() ([]home.LinkUnit, error) {
	var dict []home.LinkUnit
	var expt error
	var list []string
	var unit home.LinkUnit

	list, expt = ListBranches("frozen")
	if expt != nil {
		return dict, expt
	}
	list = append(list, "rawhide")

	for _, item := range list {
		var vers, urlx string
		var expr *regexp.Regexp

		if item == "rawhide" {
			vers = "rawhide"
		} else {
			expr = regexp.MustCompile(`f\d+`)
			vers = expr.FindString(item)
			if vers == "" {
				break
			}
		}

		urlx = fmt.Sprintf("%s/pub/fedora/linux/development/%s/Everything/x86_64/os/repodata/", config.DLSERVER, vers)
		unit = home.LinkUnit{Name: item, Link: urlx}
		dict = append(dict, unit)
		slog.Log(context.Background(), slog.LevelDebug, fmt.Sprintf("[%s] Acquired repository location for %s/%s branch at %s", item, item, vers, urlx))
		urlx = strings.Replace(urlx, "/x86_64/os/", "/source/tree/", -1)
		unit = home.LinkUnit{Name: fmt.Sprintf("src_%s", item), Link: urlx}
		dict = append(dict, unit)
		slog.Log(context.Background(), slog.LevelDebug, fmt.Sprintf("[%s] Acquired repository location for src_%s/%s branch at %s", item, item, vers, urlx))
	}

	list, expt = ListBranches("current")
	if expt != nil {
		return dict, expt
	}

	for _, item := range list {
		var vers, urlx, name string
		var expr *regexp.Regexp
		var linkbook, idenbook []string
		var fclxVers, epelVers, felnVers string
		var fclxExpr, epelExpr, felnExpr *regexp.Regexp

		expr = regexp.MustCompile(`\d+(?:\.\d+)?`)
		vers = expr.FindString(item)

		fclxExpr = regexp.MustCompile(`f\d+`)
		fclxVers = fclxExpr.FindString(item)
		epelExpr = regexp.MustCompile(`epel\d+(?:\.\d+)?`)
		epelVers = epelExpr.FindString(item)
		felnExpr = regexp.MustCompile(`epel\d-next`)
		felnVers = felnExpr.FindString(item)
		if fclxVers != "" {
			linkbook, idenbook = config.LINKDICT["Fedora Linux"], config.REPODICT["fedora"]
		} else if epelVers != "" {
			linkbook, idenbook = config.LINKDICT["Fedora EPEL"], config.REPODICT["epel"]
		} else if felnVers != "" {
			linkbook, idenbook = config.LINKDICT["Fedora EPEL Next"], config.REPODICT["epel-next"]
		}

		for indx, urli := range linkbook {
			name = fmt.Sprintf(idenbook[indx], item)
			urlx = fmt.Sprintf(urli, config.DLSERVER, vers)
			unit = home.LinkUnit{Name: name, Link: urlx}
			dict = append(dict, unit)
			slog.Log(context.Background(), slog.LevelDebug, fmt.Sprintf("[%s] Acquired repository location for %s/%s branch at %s", name, name, vers, urlx))
			urlx = strings.Replace(urlx, "/x86_64/os/", "/source/tree/", -1)
			unit = home.LinkUnit{Name: fmt.Sprintf("src_%s", name), Link: urlx}
			dict = append(dict, unit)
			slog.Log(context.Background(), slog.LevelDebug, fmt.Sprintf("[%s] Acquired repository location for src_%s/%s branch at %s", name, name, vers, urlx))
		}
	}

	unit = home.LinkUnit{Name: "koji", Link: fmt.Sprintf("%s/rawhide/latest/x86_64/repodata/", config.KOJIREPO)}
	dict = append(dict, unit)
	slog.Log(context.Background(), slog.LevelDebug, fmt.Sprintf("[%s] Acquired repository location for %s/%s branch at %s", unit.Name, unit.Name, "rawhide", unit.Link))

	slog.Log(context.Background(), slog.LevelInfo, fmt.Sprintf("%d repository location(s) acquired", len(dict)))
	return dict, nil
}
