/*
 * Copyright 2020-2021 Parakoopa and the SkyTemple Contributors
 *
 * This file is part of SkyTemple.
 *
 * SkyTemple is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * SkyTemple is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with SkyTemple.  If not, see <https://www.gnu.org/licenses/>.
 */

import React, {useState} from "react";
import Paper from "@material-ui/core/Paper";
import FormGroup from "@material-ui/core/FormGroup";
import FormControlLabel from "@material-ui/core/FormControlLabel";
import Switch from "@material-ui/core/Switch";
import {HelpButton} from "./HelpButton";
import {useSettingsStyles} from "./theme";
import NativeSelect from "@material-ui/core/NativeSelect";

export function UiSwitch(props) {
    const classes = useSettingsStyles();
    const [state, setState] = useState(props.initial)

    const handleChange = (event, newValue) => {
        setState(newValue);
    };

    return (
        <Paper className={classes.paper}>
            <FormGroup row className={classes.elem}>
                <FormControlLabel
                    control={<Switch checked={state} onChange={handleChange} id={props.id}/>}
                    label={props.label}
                />
            </FormGroup>
            <HelpButton text={props.help} title={props.label}/>
        </Paper>
    )
}