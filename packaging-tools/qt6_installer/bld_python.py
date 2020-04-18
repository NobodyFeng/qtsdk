#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2020 The Qt Company Ltd.
## Contact: https://www.qt.io/licensing/
##
## This file is part of the release tools of the Qt Toolkit.
##
## $QT_BEGIN_LICENSE:GPL-EXCEPT$
## Commercial License Usage
## Licensees holding valid commercial Qt licenses may use this file in
## accordance with the commercial license agreement provided with the
## Software or, alternatively, in accordance with the terms contained in
## a written agreement between you and The Qt Company. For licensing terms
## and conditions see https://www.qt.io/terms-conditions. For further
## information use the contact form at https://www.qt.io/contact-us.
##
## GNU General Public License Usage
## Alternatively, this file may be used under the terms of the GNU
## General Public License version 3 as published by the Free Software
## Foundation with exceptions as appearing in the file LICENSE.GPL3-EXCEPT
## included in the packaging of this file. Please review the following
## information to ensure the GNU General Public License requirements will
## be met: https://www.gnu.org/licenses/gpl-3.0.html.
##
## $QT_END_LICENSE$
##
#############################################################################

import os
import sys
import asyncio
import argparse
import platform
import multiprocessing
from shutil import which, rmtree
from logging_util import init_logger
from runner import async_exec_cmd
from installer_utils import cd, is_valid_url_path, extract_archive, download_archive


log = init_logger(__name__, debug_mode=False)


class BldPythonError(Exception):
    pass


async def prepare_sources(src: str, tmpBaseDir: str) -> str:
    log.info("Preparing sources: %s", src)
    if os.path.isdir(src):
        return src
    srcTmpDir = os.path.join(tmpBaseDir, "src_dir")
    rmtree(srcTmpDir, ignore_errors=True)
    os.makedirs(srcTmpDir)
    if os.path.isfile(src):
        await extract_archive(src, srcTmpDir)
    elif is_valid_url_path(src):
        destFile = download_archive(src, tmpBaseDir)
        await extract_archive(destFile, srcTmpDir)
    else:
        raise BldPythonError("Could not prepare sources from: {0}".format(src))
    return srcTmpDir


def locate_source_root(searchDir: str) -> str:
    for root, dirs, files in os.walk(searchDir):
        if "configure" in files and os.path.isfile(os.path.join(root, "configure")):
            return root
    raise BldPythonError("Could not find source root directory from: {0}".format(searchDir))


async def _build_python(srcDir: str, bldDir: str, prefix: str) -> str:
    log.info("Building..")
    log.info("  Source dir: %s", srcDir)
    log.info("  Build dir: %s", bldDir)
    log.info("  Prefix: %s", prefix)
    system = platform.system().lower()
    cpuCount = str(multiprocessing.cpu_count())
    if "windows" in system:
        configureCmd = [os.path.join(srcDir, 'configure'), '--enable-shared', '--prefix=' + prefix]
        makeCmd = ['nmake']
        makeInstallCmd = ['nmake', 'install']
    elif "darwin" in system:
        configureCmd = [os.path.join(srcDir, 'configure'), '--enable-framework', '--with-openssl=$(brew --prefix openssl)', '--prefix=' + prefix]
        makeCmd = ['make', '-j' + cpuCount]
        makeInstallCmd = ['make', 'install']
    else:
        configureCmd = [os.path.join(srcDir, 'configure'), '--enable-shared', '--prefix=' + prefix]
        makeCmd = ['make', '-j' + cpuCount]
        makeInstallCmd = ['make', 'install']

    rmtree(bldDir, ignore_errors=True)
    os.makedirs(bldDir)

    with cd(bldDir):
        await async_exec_cmd(configureCmd)
        await async_exec_cmd(makeCmd)
        await async_exec_cmd(makeInstallCmd)
    log.info("Python built successfully and installed to: %s", prefix)
    return prefix


async def build_python(src: str, prefix: str) -> str:
    if os.path.isdir(prefix):
        log.info("Deleting existing Python build from: %s", prefix)
        rmtree(prefix, ignore_errors=True)
    baseDir = os.path.join(os.getcwd(), "python_bld_tmp")
    os.makedirs(baseDir, exist_ok=True)
    srcDir = await prepare_sources(src, baseDir)
    bldDir = os.path.join(baseDir, "build_dir")
    sourceRootDir = locate_source_root(srcDir)
    return await _build_python(sourceRootDir, bldDir, prefix)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog="Script to build Python from sources")
    parser.add_argument("--src", dest="src", type=str, default=os.getenv("PYTHON_SRC"), help="Path to local checkout or .zip/.7z/.tar.gz")
    parser.add_argument("--prefix", dest="prefix", type=str, default=os.path.join(os.path.expanduser("~"), "_python_bld"))
    args = parser.parse_args(sys.argv[1:])

    for requiredTool in ["7z", "tar"]:
        if not which(requiredTool):
            log.error("Could not find '{0}' from the system. This tool is needed. Aborting..".format(requiredTool))
            sys.exit(1)

    loop = asyncio.get_event_loop()
    loop.run_until_complete(build_python(args.src, args.prefix))
