package driver

import (
	"context"
	"crypto/rand"
	"fmt"
	"log/slog"
	"metasource/metasource/config"
	"metasource/metasource/models"
	"os"
	"strings"
)

func GenerateIdentity(length *int64) string {
	randBytes := make([]byte, *length/2)
	_, _ = rand.Read(randBytes)

	return fmt.Sprintf("%x", randBytes)
}

var InitPath = func(vers *string, loca *string) error {
	var expt error

	_, expt = os.Stat(*loca)
	if os.IsNotExist(expt) {
		expt = os.MkdirAll(fmt.Sprintf("%s/sxml", *loca), 0750)
		if expt != nil {
			return expt
		}
		expt = os.MkdirAll(fmt.Sprintf("%s/sxml", *loca), 0750)
		if expt != nil {
			return expt
		}
		expt = os.MkdirAll(fmt.Sprintf("%s/comp", *loca), 0750)
		if expt != nil {
			return expt
		}
	}

	slog.Log(context.Background(), slog.LevelDebug, fmt.Sprintf("[%s] Directories initialized", *vers))
	return nil
}

func KillTemp(vers *string, loca *string) error {
	var expt error

	expt = TransferResult(vers, loca)
	if expt != nil {
		return expt
	}

	expt = os.RemoveAll(*loca)
	if expt != nil {
		return expt
	}

	slog.Log(context.Background(), slog.LevelDebug, fmt.Sprintf("[%s] Directories removed", *vers))
	return nil
}

func TransferResult(vers *string, loca *string) error {
	var expt error
	var files []os.DirEntry
	var oldPath, newPath string

	files, expt = os.ReadDir(*loca)
	if expt != nil {
		return expt
	}

	for _, file := range files {
		if strings.HasPrefix(file.Name(), "metasource-") && strings.HasSuffix(file.Name(), ".sqlite") {
			oldPath = fmt.Sprintf("%s/%s", *loca, file.Name())
			newPath = fmt.Sprintf("%s/../%s", *loca, file.Name())
			expt = os.Rename(oldPath, newPath)
			if expt != nil {
				return expt
			}
		}
	}

	slog.Log(context.Background(), slog.LevelDebug, fmt.Sprintf("[%s] Results transferred", *vers))
	return nil
}

func findBranchName(name string) string {
	name = strings.Replace(name, "src_", "", 1)
	name = strings.Replace(name, "-updates-testing", "", 1)
	name = strings.Replace(name, "-updates", "", 1)
	name = strings.Replace(name, "-testing", "", 1)
	return name
}

var KillObsoleteBranches = func(active []models.LinkUnit) error {
	var expt error
	var files []os.DirEntry

	activeBranches := make(map[string]bool)
	for _, unit := range active {
		activeBranches[findBranchName(unit.Name)] = true
	}

	files, expt = os.ReadDir(config.DBFOLDER)
	if expt != nil {
		return expt
	}

	for _, file := range files {
		if file.IsDir() || !strings.HasPrefix(file.Name(), "metasource-") || !strings.HasSuffix(file.Name(), ".sqlite") {
			continue
		}

		name := file.Name()
		name = strings.Replace(name, "metasource-", "", 1)
		name = strings.Replace(name, "-primary.sqlite", "", 1)
		name = strings.Replace(name, "-filelists.sqlite", "", 1)
		name = strings.Replace(name, "-other.sqlite", "", 1)
		branch := findBranchName(name)

		if !activeBranches[branch] {
			path := fmt.Sprintf("%s/%s", config.DBFOLDER, file.Name())
			expt = os.Remove(path)
			if expt != nil {
				slog.Log(context.Background(), slog.LevelWarn, fmt.Sprintf("Failed to remove stale database file %s due to %s", file.Name(), expt.Error()))
				continue
			}
			slog.Log(context.Background(), slog.LevelInfo, fmt.Sprintf("Purged obsolete database file %s (branch %s)", file.Name(), branch))
		}
	}

	return nil
}
