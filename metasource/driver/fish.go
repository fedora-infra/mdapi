package driver

import (
	"context"
	"fmt"
	"github.com/klauspost/compress/gzip"
	"github.com/klauspost/compress/zstd"
	"github.com/ulikunitz/xz"
	"io"
	"log/slog"
	"metasource/metasource/models/home"
	"os"
	"path/filepath"
	"strings"
	"sync"
)

func WithdrawArchives(unit *home.FileUnit, vers *string, wait *sync.WaitGroup, cast *int, loca *string) {
	defer wait.Done()

	var inpt, otpt *os.File
	var expt error
	var path string
	var name string

	list := strings.Split(unit.Name, ".")
	name = strings.Replace(unit.Name, fmt.Sprintf(".%s", list[len(list)-1]), "", -1)

	inpt, expt = os.Open(unit.Path)
	if expt != nil {
		unit.Keep = false
		slog.Log(context.Background(), slog.LevelDebug, fmt.Sprintf("[%s] Extraction failed for %s due to %s", *vers, name, expt.Error()))
		return
	}
	defer inpt.Close()

	path = filepath.Clean(filepath.Join(*loca, "/sxml/", name))

	otpt, expt = os.Create(path) // #nosec G304 -- path is verified and cleaned
	if expt != nil {
		unit.Keep = false
		slog.Log(context.Background(), slog.LevelDebug, fmt.Sprintf("[%s] Extraction failed for %s due to %s", *vers, name, expt.Error()))
		return
	}
	defer otpt.Close()

	if strings.HasSuffix(unit.Name, ".gz") {
		var read *gzip.Reader

		read, expt = gzip.NewReader(inpt)
		if expt != nil {
			unit.Keep = false
			slog.Log(context.Background(), slog.LevelDebug, fmt.Sprintf("[%s] Extraction failed for %s due to %s", *vers, name, expt.Error()))
			return
		}
		defer read.Close()

		_, expt = io.Copy(otpt, read)
		if expt != nil {
			unit.Keep = false
			slog.Log(context.Background(), slog.LevelDebug, fmt.Sprintf("[%s] Extraction failed for %s due to %s", *vers, name, expt.Error()))
			return
		}

	} else if strings.HasSuffix(unit.Name, ".zst") {
		var read *zstd.Decoder

		read, expt = zstd.NewReader(inpt)
		if expt != nil {
			unit.Keep = false
			slog.Log(context.Background(), slog.LevelDebug, fmt.Sprintf("[%s] Extraction failed for %s due to %s", *vers, name, expt.Error()))
			return
		}
		defer read.Close()

		_, expt = io.Copy(otpt, read)
		if expt != nil {
			unit.Keep = false
			slog.Log(context.Background(), slog.LevelDebug, fmt.Sprintf("[%s] Extraction failed for %s due to %s", *vers, name, expt.Error()))
			return
		}
	} else if strings.HasSuffix(unit.Name, ".xz") {
		var read *xz.Reader

		read, expt = xz.NewReader(inpt)
		if expt != nil {
			unit.Keep = false
			slog.Log(context.Background(), slog.LevelDebug, fmt.Sprintf("[%s] Extraction failed for %s due to %s", *vers, name, expt.Error()))
			return
		}

		_, expt = io.Copy(otpt, read)
		if expt != nil {
			unit.Keep = false
			slog.Log(context.Background(), slog.LevelDebug, fmt.Sprintf("[%s] Extraction failed for %s due to %s", *vers, name, expt.Error()))
			return
		}
	}

	unit.Keep = true
	unit.Name = name
	unit.Path = path
	*cast++
	slog.Log(context.Background(), slog.LevelDebug, fmt.Sprintf("[%s] Extraction complete for %s", *vers, name))
}
