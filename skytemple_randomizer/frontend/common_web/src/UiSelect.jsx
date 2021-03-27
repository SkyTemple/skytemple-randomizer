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

import {useSettingsStyles} from "./theme";
import React, {useState} from "react";
import Paper from "@material-ui/core/Paper";
import FormControl from "@material-ui/core/FormControl";
import InputLabel from "@material-ui/core/InputLabel";
import NativeSelect from "@material-ui/core/NativeSelect";
import {HelpButton} from "./HelpButton";

export function UiSelect(props) {
    const classes = useSettingsStyles();
    const [state, setState] = useState(props.initial)

    const handleChange = (event) => {
        setState(event.target.value);
    };
    const items = [];
    for (const option in props.options) {
        const optionLabel = props.options[option]
        items.push(
            <option value={option}>{optionLabel}</option>
        )
    }
    return (
        <Paper className={classes.paper}>
            <FormControl className={classes.formControl}>
                <InputLabel id={props.id + '-label'}>{props.label}</InputLabel>
                <NativeSelect
                    labelId="demo-simple-select-label"
                    id="demo-simple-select"
                    value={state}
                    onChange={handleChange}
                    className={classes.elem}
                >
                    {items}
                </NativeSelect>
            </FormControl>
            <HelpButton text={props.help} title={props.label}/>
        </Paper>
    )
}