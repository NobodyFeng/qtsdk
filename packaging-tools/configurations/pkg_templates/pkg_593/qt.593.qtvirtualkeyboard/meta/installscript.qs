/****************************************************************************
**
** Copyright (C) 2017 The Qt Company Ltd.
** Contact: https://www.qt.io/licensing/
**
** This file is part of the release tools of the Qt Toolkit.
**
** $QT_BEGIN_LICENSE:GPL-EXCEPT$
** Commercial License Usage
** Licensees holding valid commercial Qt licenses may use this file in
** accordance with the commercial license agreement provided with the
** Software or, alternatively, in accordance with the terms contained in
** a written agreement between you and The Qt Company. For licensing terms
** and conditions see https://www.qt.io/terms-conditions. For further
** information use the contact form at https://www.qt.io/contact-us.
**
** GNU General Public License Usage
** Alternatively, this file may be used under the terms of the GNU
** General Public License version 3 as published by the Free Software
** Foundation with exceptions as appearing in the file LICENSE.GPL3-EXCEPT
** included in the packaging of this file. Please review the following
** information to ensure the GNU General Public License requirements will
** be met: https://www.gnu.org/licenses/gpl-3.0.html.
**
** $QT_END_LICENSE$
**
****************************************************************************/

// constructor
function Component()
{
    if (installer.isOfflineOnly())
        component.setValue("Default", "true");
    // Determine if this is a online snapshot build
    var snapshotBuild = false;
    var isSnapshotStr = "%ONLINE_SNAPSHOT_BUILD%";
    if (['true', 'yes', '1'].indexOf(isSnapshotStr) >= 0)
        snapshotBuild = true;

    if (snapshotBuild) {
        // Add automatic dependency for preview component
        var autoDependency = component.value("AutoDependOn");
        var dependencyStr = "preview.qt.59.qtvirtualkeyboard";
        if (autoDependency) {
            component.setValue("AutoDependOn", autoDependency+","+dependencyStr)
        }
        else {
            component.setValue("AutoDependOn", dependencyStr)
        }
    }
}

Component.prototype.createOperations = function()
{
    component.createOperations();
}
