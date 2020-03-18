/****************************************************************************
**
** Copyright (C) 2014 Digia Plc and/or its subsidiary(-ies).
** Contact: http://www.qt-project.org/legal
**
** This file is part of the release tools of the Qt Toolkit.
**
** $QT_BEGIN_LICENSE:LGPL$
** Commercial License Usage
** Licensees holding valid commercial Qt licenses may use this file in
** accordance with the commercial license agreement provided with the
** Software or, alternatively, in accordance with the terms contained in
** a written agreement between you and Digia.  For licensing terms and
** conditions see http://qt.digia.com/licensing.  For further information
** use the contact form at http://qt.digia.com/contact-us.
**
** GNU Lesser General Public License Usage
** Alternatively, this file may be used under the terms of the GNU Lesser
** General Public License version 2.1 as published by the Free Software
** Foundation and appearing in the file LICENSE.LGPL included in the
** packaging of this file.  Please review the following information to
** ensure the GNU Lesser General Public License version 2.1 requirements
** will be met: http://www.gnu.org/licenses/old-licenses/lgpl-2.1.html.
**
** In addition, as a special exception, Digia gives you certain additional
** rights.  These rights are described in the Digia Qt LGPL Exception
** version 1.1, included in the file LGPL_EXCEPTION.txt in this package.
**
** GNU General Public License Usage
** Alternatively, this file may be used under the terms of the GNU
** General Public License version 3.0 as published by the Free Software
** Foundation and appearing in the file LICENSE.GPL included in the
** packaging of this file.  Please review the following information to
** ensure the GNU General Public License version 3.0 requirements will be
** met: http://www.gnu.org/copyleft/gpl.html.
**
**
** $QT_END_LICENSE$
**
****************************************************************************/

// constructor
function Component()
{
    // only install c runtime if it is needed, no minor version check of the c runtime till we need it
    if (installer.value("HKEY_LOCAL_MACHINE\\SOFTWARE\\Microsoft\\VisualStudio\\10.0\\VC\\VCRedist\\x64\\Installed") != 1)
        component.setValue("RequiresAdminRights", "true");
}

Component.prototype.createOperations = function()
{
    // Call the base createOperations and afterwards set some registry settings
    // so that the simulator finds its fonts and applications find the simulator
    component.createOperations();

    if (installer.value("HKEY_LOCAL_MACHINE\\SOFTWARE\\Microsoft\\VisualStudio\\10.0\\VC\\VCRedist\\x64\\Installed") != 1) {
        // return value 3010 means it need a reboot, but in most cases it is not needed for run Qt application
        // return value 5100 means there's a newer version of the runtime already installed
        component.addElevatedOperation("Execute", "{0,3010,1638,5100}", "@TargetDir@\\vcredist\\vcredist_x64.exe", "/norestart", "/q");
    }
}
