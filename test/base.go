package test

import (
	"fmt"
	"github.com/klauspost/compress/gzip"
	"github.com/klauspost/compress/zstd"
	"github.com/ulikunitz/xz"
	"io"
	"metasource/metasource/config"
	"metasource/metasource/driver"
	"os"
	"testing"
)

func WipeGeneration(loca string) {
	_, expt := os.Stat(loca)
	if expt != nil {
		return
	} else {
		_ = os.RemoveAll(loca)
	}
}

func CopyGeneration(srce string, dest string) error {
	srcedata, expt := os.ReadFile(srce) // #nosec G304 -- path is verified and cleaned
	if expt != nil {
		return expt
	}
	expt = os.WriteFile(dest, srcedata, 0600)
	if expt != nil {
		return expt
	}
	return nil
}

func Path_UnInit(t *testing.T, temp string) {
	t.Helper()

	origpath := config.DBFOLDER
	config.DBFOLDER = temp

	t.Cleanup(func() {
		config.DBFOLDER = origpath
	})
}

func Path_Archived_ZSTD(t *testing.T, iden string) {
	t.Helper()

	origpath := config.DBFOLDER
	basepath := "./assets"
	destpath := fmt.Sprintf("%s/test-%s", basepath, iden)
	_ = os.MkdirAll(destpath, 0750)
	for _, item := range []string{"primary", "filelists", "other"} {
		srcefile, _ := os.Open(fmt.Sprintf("%s/%s", basepath, fmt.Sprintf("testbase_%s.xml", item)))
		defer srcefile.Close()
		destfile, _ := os.Create(fmt.Sprintf("%s/%s", destpath, fmt.Sprintf("metasource-rawhide-%s.xml.zst", item)))
		defer destfile.Close()
		zstdmake, _ := zstd.NewWriter(destfile, zstd.WithEncoderLevel(zstd.EncoderLevelFromZstd(22)))
		defer zstdmake.Close()
		_, _ = io.Copy(zstdmake, srcefile)
	}
	config.DBFOLDER = destpath

	t.Cleanup(func() {
		config.DBFOLDER = origpath
		WipeGeneration(destpath)
	})
}

func Path_Archived_FaultyFile(t *testing.T, iden string, extn string) {
	t.Helper()

	origpath := config.DBFOLDER
	basepath := "./assets"
	destpath := fmt.Sprintf("%s/test-%s", basepath, iden)
	sxmlpath := fmt.Sprintf("%s/sxml", destpath)
	_, _ = os.MkdirAll(destpath, 0750), os.MkdirAll(sxmlpath, 0750)
	for _, item := range []string{"primary", "filelists", "other"} {
		_ = CopyGeneration(
			fmt.Sprintf("%s/%s", basepath, fmt.Sprintf("testbase_%s.xml", item)),
			fmt.Sprintf("%s/%s", destpath, fmt.Sprintf("metasource-rawhide-%s.xml.%s", item, extn)),
		)
	}
	config.DBFOLDER = destpath

	t.Cleanup(func() {
		config.DBFOLDER = origpath
		WipeGeneration(destpath)
	})
}

func Path_Archived_XZ(t *testing.T, iden string) {
	t.Helper()

	origpath := config.DBFOLDER
	basepath := "./assets"
	destpath := fmt.Sprintf("%s/test-%s", basepath, iden)
	_ = os.MkdirAll(destpath, 0750)
	for _, item := range []string{"primary", "filelists", "other"} {
		srcefile, _ := os.Open(fmt.Sprintf("%s/%s", basepath, fmt.Sprintf("testbase_%s.xml", item)))
		defer srcefile.Close()
		destfile, _ := os.Create(fmt.Sprintf("%s/%s", destpath, fmt.Sprintf("metasource-rawhide-%s.xml.xz", item)))
		defer destfile.Close()
		xzauthor, _ := xz.NewWriter(destfile)
		defer xzauthor.Close()
		_, _ = io.Copy(xzauthor, srcefile)
	}
	config.DBFOLDER = destpath

	t.Cleanup(func() {
		config.DBFOLDER = origpath
		WipeGeneration(destpath)
	})
}

func Path_Archived_GZ(t *testing.T, iden string) {
	t.Helper()

	origpath := config.DBFOLDER
	basepath := "./assets"
	destpath := fmt.Sprintf("%s/test-%s", basepath, iden)
	_ = os.MkdirAll(destpath, 0750)
	for _, item := range []string{"primary", "filelists", "other"} {
		srcefile, _ := os.Open(fmt.Sprintf("%s/%s", basepath, fmt.Sprintf("testbase_%s.xml", item)))
		defer srcefile.Close()
		destfile, _ := os.Create(fmt.Sprintf("%s/%s", destpath, fmt.Sprintf("metasource-rawhide-%s.xml.gz", item)))
		defer destfile.Close()
		gzauthor, _ := gzip.NewWriterLevel(destfile, gzip.BestCompression)
		defer gzauthor.Close()
		_, _ = io.Copy(gzauthor, srcefile)
	}
	config.DBFOLDER = destpath

	t.Cleanup(func() {
		config.DBFOLDER = origpath
		WipeGeneration(destpath)
	})
}

func Path_Init(t *testing.T, repo string) {
	t.Helper()

	origpath := config.DBFOLDER
	basepath := "./assets"
	destpath := fmt.Sprintf("%s/test-%s", basepath, driver.GenerateIdentity(&config.RANDOM_LENGTH))
	_ = os.MkdirAll(destpath, 0750)
	for _, item := range []string{"primary", "filelists", "other"} {
		destname := fmt.Sprintf("metasource-rawhide-%s.sqlite", item)
		if repo != "" {
			destname = fmt.Sprintf("metasource-rawhide-%s-%s.sqlite", repo, item)
		}
		_ = CopyGeneration(
			fmt.Sprintf("%s/%s", basepath, fmt.Sprintf("testbase_%s.sqlite", item)),
			fmt.Sprintf("%s/%s", destpath, destname),
		)
	}
	config.DBFOLDER = destpath

	t.Cleanup(func() {
		config.DBFOLDER = origpath
		WipeGeneration(destpath)
	})
}

func Path_Init_Faulty(t *testing.T) {
	t.Helper()

	origpath := config.DBFOLDER
	basepath := "./assets"
	destpath := fmt.Sprintf("%s/test-%s", basepath, driver.GenerateIdentity(&config.RANDOM_LENGTH))
	_ = os.MkdirAll(destpath, 0750)
	for _, item := range []string{"primary", "filelists", "other"} {
		_ = CopyGeneration(
			fmt.Sprintf("%s/%s", basepath, fmt.Sprintf("testbase_%s.xml", item)),
			fmt.Sprintf("%s/%s", destpath, fmt.Sprintf("metasource-rawhide-%s.sqlite", item)),
		)
	}
	config.DBFOLDER = destpath

	t.Cleanup(func() {
		config.DBFOLDER = origpath
		WipeGeneration(destpath)
	})
}

func Path_Init_Vacant(t *testing.T) {
	t.Helper()

	origpath := config.DBFOLDER
	basepath := "./assets"
	destpath := fmt.Sprintf("%s/test-%s", basepath, driver.GenerateIdentity(&config.RANDOM_LENGTH))
	comppath := fmt.Sprintf("%s/comp", destpath)
	sxmlpath := fmt.Sprintf("%s/sxml", destpath)
	_, _, _ = os.MkdirAll(destpath, 0750), os.MkdirAll(comppath, 0750), os.MkdirAll(sxmlpath, 0750)
	config.DBFOLDER = destpath

	t.Cleanup(func() {
		config.DBFOLDER = origpath
		WipeGeneration(destpath)
	})
}
