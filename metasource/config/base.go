package config

import (
	"github.com/lmittmann/tint"
	"log/slog"
	"os"
)

func SetLogger(lglvtext *string) {
	var lglvoptn slog.Level

	switch *lglvtext {
	case "info":
		lglvoptn = slog.LevelInfo
	case "warn":
		lglvoptn = slog.LevelWarn
	case "debug":
		lglvoptn = slog.LevelDebug
	default:
		lglvoptn = slog.LevelInfo
	}

	logger := slog.New(tint.NewHandler(os.Stdout, &tint.Options{
		Level: lglvoptn,
	}))
	slog.SetDefault(logger)
}

var BODHIURL string = "https://bodhi.fedoraproject.org"
var KOJIREPO string = "https://kojipkgs.fedoraproject.org/repos"
var DLSERVER string = "https://dl.fedoraproject.org"

var LINKDICT = map[string][]string{
	"Fedora Linux": {
		"%s/pub/fedora/linux/releases/%s/Everything/x86_64/os/repodata/",
		"%s/pub/fedora/linux/updates/%s/Everything/x86_64/repodata/",
		"%s/pub/fedora/linux/updates/testing/%s/Everything/x86_64/repodata/",
	},
	"Fedora EPEL": {
		"%s/pub/epel/%s/Everything/x86_64/repodata/",
		"%s/pub/epel/testing/%s/Everything/x86_64/repodata/",
	},
	"Fedora EPEL Next": {
		"%s/pub/epel/next/%s/Everything/x86_64/repodata/",
		"%s/pub/epel/next/testing/%s/Everything/x86_64/repodata/",
	},
}

var REPODICT = map[string][]string{
	"fedora":    {"%s", "%s-updates", "%s-updates-testing"},
	"epel":      {"%s", "%s-testing"},
	"epel-next": {"%s", "%s-testing"},
}

var ASSETSDB string = "assets"

var DBFOLDER string = "/var/tmp/metasource"

var WAITTIME int = 10

var FILENAME string = "metasource-%s-%s"

var ATTEMPTS int64 = 4

var DBDRIVER string = "sqlite3"

var RANDOM_LENGTH int64 = 8

// SQLite3 queries for various purposes

var SIGNAL_DATABASE string = "CREATE INDEX packageSource ON packages (rpm_sourcerpm)"

var OBTAIN_RELATION_LIST string = "SELECT name FROM sqlite_master WHERE type='table'"

var RELATION_QUERY string = "SELECT {table}.name, {table}.flags, {table}.epoch, {table}.version, {table}.release, packages.name FROM {table}, packages WHERE {table}.pkgKey == packages.pkgKey;"

var FILEUNIT_QUERY string = "SELECT {table}.name, {table}.type, packages.name FROM {table}, packages WHERE {table}.pkgKey == packages.pkgKey;"

var FILELIST_QUERY string = "SELECT packages.pkgId, {table}.dirname, {table}.filenames, {table}.filetypes FROM {table}, packages WHERE {table}.pkgKey == packages.pkgKey;"

var PACKAGES_QUERY string = "SELECT {table}.name, {table}.version, {table}.release, {table}.epoch, {table}.arch FROM {table};"

var STANDARD_QUERY string = "SELECT * from {table};"

var CHANGELOG_QUERY string = "SELECT packages.pkgId, {table}.author, {table}.date, {table}.changelog FROM {table}, packages WHERE {table}.pkgKey == packages.pkgKey;"

var PKGCACHE_BUILDER string = "SELECT {table}.pkgId, {table}.name FROM {table};"

var QURYDICT = map[string]string{
	"conflicts":   RELATION_QUERY,
	"enhances":    RELATION_QUERY,
	"obsoletes":   RELATION_QUERY,
	"provides":    RELATION_QUERY,
	"requires":    RELATION_QUERY,
	"supplements": RELATION_QUERY,
	"recommends":  RELATION_QUERY,
	"suggests":    RELATION_QUERY,
	"files":       FILEUNIT_QUERY,
	"packages":    PACKAGES_QUERY,
	"changelog":   CHANGELOG_QUERY,
	"filelist":    FILELIST_QUERY,
}

// SQLite3 queries for various endpoints

var OBTAIN_PACKAGE string = "SELECT pkgKey, pkgId, name, rpm_sourcerpm, epoch, version, release, arch, summary, description, url FROM packages WHERE name = ? ORDER BY epoch DESC, version DESC, release DESC"

var OBTAIN_PACKAGE_INFO string = "SELECT rowid, pkgKey, name, epoch, version, release, flags FROM %s WHERE pkgKey = ?"

var OBTAIN_CO_PACKAGE string = "SELECT DISTINCT(name) FROM packages WHERE rpm_sourcerpm = ?"

var OBTAIN_PACKAGE_BY_SOURCE string = "SELECT pkgKey, pkgId, name, rpm_sourcerpm, epoch, version, release, arch, summary, description, url FROM packages WHERE rpm_sourcerpm LIKE ? ORDER BY epoch DESC, version DESC, release DESC"

var OBTAIN_PACKAGE_BY string = "SELECT p.pkgKey, p.pkgId, p.name, p.rpm_sourcerpm, p.epoch, p.version, p.release, p.arch, p.summary, p.description, p.url FROM packages p JOIN %s t ON t.pkgKey = p.pkgKey WHERE t.name = ? ORDER BY p.epoch DESC, p.version DESC, p.release DESC"

var OBTAIN_FILEUNIT string = "SELECT f.pkgKey, f.dirname, f.filenames, f.filetypes FROM filelist f JOIN packages p ON p.pkgId = ? WHERE f.pkgKey = p.pkgKey ORDER BY f.filenames"

var OBTAIN_CHANGELOGS string = "SELECT c.pkgKey, c.author, c.changelog, c.date FROM changelog c JOIN packages p ON p.pkgId = ? WHERE c.pkgKey = p.pkgKey ORDER BY c.date DESC"
