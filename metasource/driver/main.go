package driver

import (
	"context"
	"fmt"
	"log/slog"
	"metasource/metasource/models"
)

func Database() error {
	var expt error
	var list []models.LinkUnit
	var item models.LinkUnit

	list, expt = PopulateRepositories()
	if expt != nil {
		return expt
	}

	expt = KillObsoleteBranches(list)
	if expt != nil {
		slog.Log(context.Background(), slog.LevelWarn, fmt.Sprintf("Purging obsolete branches failed due to %s", expt.Error()))
	}

	for _, item = range list {
		expt = HandleRepositories(&item)
		if expt != nil {
			slog.Log(context.Background(), slog.LevelWarn, fmt.Sprintf("[%s] Repository handling failed due to %s", item.Name, expt.Error()))
		}
	}

	return nil
}
