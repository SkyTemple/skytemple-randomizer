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
import {Slider} from "@material-ui/core";
import Typography from "@material-ui/core/Typography";

export function UiSlider(props) {
    const classes = useSettingsStyles();
    const [state, setState] = useState(props.initial)

    const handleChange = (event, newValue) => {
        setState(Math.ceil(newValue));
        props.onChange(props.id, Math.ceil(newValue));
    };
    return (
        <Paper className={classes.paper}>
            <FormControl className={classes.formControl}>
                <Typography id={props.id + '-label'}>{props.label}</Typography>
                <div style={{width: '500px', maxWidth: '100%'}}>
                    <Slider
                      defaultValue={state}
                      step={1}
                      min={0}
                      max={props.max}
                      valueLabelDisplay="auto"
                      onChange={handleChange}
                    />
                </div>
            </FormControl>
            <HelpButton text={props.help} title={props.label}/>
        </Paper>
    )
}