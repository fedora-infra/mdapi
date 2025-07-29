package reader

/*
#cgo pkg-config: createrepo_c
#include "createrepo_c/xml_parser.h"
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

func MakeDatabase(vers *string, cast *int, prmyinpt *string, fileinpt *string, othrinpt *string, prmyname *string, filename *string, othrname *string, prmypath *string, filepath *string, othrpath *string) (int, error) {
	var gexp *C.GError
	var expt error
	var iter *C.cr_PkgIterator
	var wait sync.WaitGroup
	var prmyconv, fileconv, othrconv *C.char
	var prmypack, filepack, othrpack chan *C.cr_Package
	var prmydone, filedone, othrdone chan bool
	var prmyover, fileover, othrover chan bool
	var prmyover_main, fileover_main, othrover_main bool
	var pack *C.cr_Package
	var numb int
	var head string

	prmyconv = C.CString(*prmyinpt)
	fileconv = C.CString(*fileinpt)
	othrconv = C.CString(*othrinpt)
	defer C.free(unsafe.Pointer(prmyconv))
	defer C.free(unsafe.Pointer(fileconv))
	defer C.free(unsafe.Pointer(othrconv))

	prmypack, filepack, othrpack = make(chan *C.cr_Package, 1), make(chan *C.cr_Package, 1), make(chan *C.cr_Package, 1)
	prmydone, filedone, othrdone = make(chan bool, 1), make(chan bool, 1), make(chan bool, 1)
	prmyover, fileover, othrover = make(chan bool, 1), make(chan bool, 1), make(chan bool, 1)

	wait.Add(3)
	go PopulatePrmy(vers, &wait, cast, prmyname, prmypath, prmypack, prmydone, prmyover)
	go PopulateFile(vers, &wait, cast, filename, filepath, filepack, filedone, fileover)
	go PopulateOthr(vers, &wait, cast, othrname, othrpath, othrpack, othrdone, othrover)

	prmyover_main = <-prmyover
	fileover_main = <-fileover
	othrover_main = <-othrover

	close(prmyover)
	close(fileover)
	close(othrover)

	prmyover, fileover, othrover = nil, nil, nil

	if prmyover_main || fileover_main || othrover_main {
		expt = fmt.Errorf("metadata databases already exist or opening failed")
		slog.Log(context.Background(), slog.LevelDebug, fmt.Sprintf("[%s] Database generation failed due to %s", *vers, expt.Error()))
		return numb, expt
	}

	iter = C.cr_PkgIterator_new(prmyconv, fileconv, othrconv, nil, nil, nil, nil, &gexp)
	if iter == nil {
		expt = fmt.Errorf("%s", C.GoString(gexp.message))
		slog.Log(context.Background(), slog.LevelDebug, fmt.Sprintf("[%s] Database generation failed due to %s", *vers, expt.Error()))
		return numb, expt
	}
	defer C.cr_PkgIterator_free(iter, &gexp)

	for C.cr_PkgIterator_is_finished(iter) == 0 {
		var prmydone_main, filedone_main, othrdone_main bool

		pack = C.cr_PkgIterator_parse_next(iter, &gexp)
		if pack == nil {
			break
		}

		prmypack <- pack
		filepack <- pack
		othrpack <- pack

		prmydone_main = <-prmydone
		filedone_main = <-filedone
		othrdone_main = <-othrdone

		if prmydone_main && filedone_main && othrdone_main {
			numb += 1
			head = fmt.Sprintf("%s %s:%s-%s.%s", C.GoString(pack.name), C.GoString(pack.epoch), C.GoString(pack.version), C.GoString(pack.release), C.GoString(pack.arch))
			slog.Log(context.Background(), slog.LevelDebug, fmt.Sprintf("[%s] %s added.", *vers, head))
		}

		C.cr_package_free(pack)
	}

	close(prmypack)
	close(filepack)
	close(othrpack)
	close(prmydone)
	close(filedone)
	close(othrdone)

	prmypack, filepack, othrpack = nil, nil, nil
	prmydone, filedone, othrdone = nil, nil, nil

	wait.Wait()

	if gexp != nil {
		C.g_error_free(gexp)
	}

	slog.Log(context.Background(), slog.LevelDebug, fmt.Sprintf("[%s] Database generation complete with %d package(s)", *vers, numb))
	return numb, nil
}
