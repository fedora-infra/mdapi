package reader

/*
#cgo pkg-config: createrepo_c
#include "createrepo_c/sqlite.h"
#include "createrepo_c/package.h"
*/
import "C"
import (
	"context"
	"fmt"
	"log/slog"
	"sync"
	"unsafe"
)

func PopulateOthr(vers *string, wait *sync.WaitGroup, cast *int, name *string, path *string, dbpk <-chan *C.cr_Package, done chan<- bool, over chan<- bool) {
	defer wait.Done()

	var conv *C.char
	var base *C.cr_SqliteDb
	var pack *C.cr_Package
	var rslt int
	var gexp *C.GError
	var expt error

	conv = C.CString(*path)
	defer C.free(unsafe.Pointer(conv))

	base = C.cr_db_open(conv, C.CR_DB_OTHER, &gexp)
	defer C.cr_db_close(base, &gexp)
	if gexp != nil {
		expt = fmt.Errorf("%s", C.GoString(gexp.message))
		slog.Log(context.Background(), slog.LevelDebug, fmt.Sprintf("[%s] Database generation failed due to %s", *vers, expt.Error()))
		over <- true
		return
	} else {
		over <- false
	}

	for pack = range dbpk {
		rslt = int(C.cr_db_add_pkg(base, pack, &gexp))
		if rslt != 0 {
			expt = fmt.Errorf("%s", C.GoString(gexp.message))
			slog.Log(context.Background(), slog.LevelDebug, fmt.Sprintf("[%s] Database generation failed due to %s", *vers, expt.Error()))
			done <- false
		} else {
			done <- true
		}
	}

	if gexp != nil {
		C.g_error_free(gexp)
	}

	*cast++
	slog.Log(context.Background(), slog.LevelDebug, fmt.Sprintf("[%s] Database generation complete for %s", *vers, *name))
}
