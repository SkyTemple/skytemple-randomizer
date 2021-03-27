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

import React, {Fragment, useState} from "react";
import TableCell from "@material-ui/core/TableCell";
import Switch from "@material-ui/core/Switch";
import TableRow from "@material-ui/core/TableRow";
import Paper from "@material-ui/core/Paper";
import Toolbar from "@material-ui/core/Toolbar";
import Typography from "@material-ui/core/Typography";
import {HelpButton} from "./HelpButton";
import TableContainer from "@material-ui/core/TableContainer";
import Table from "@material-ui/core/Table";
import TableHead from "@material-ui/core/TableHead";
import TableBody from "@material-ui/core/TableBody";
import {useSettingsStyles} from "./theme";
import ButtonGroup from "@material-ui/core/ButtonGroup";
import IconButton from "@material-ui/core/IconButton";
import {Close, Info, Settings} from "@material-ui/icons";
import Button from "@material-ui/core/Button";
import Dialog from "@material-ui/core/Dialog";
import Slide from "@material-ui/core/Slide";
import AppBar from "@material-ui/core/AppBar";
import Grid from "@material-ui/core/Grid";

const Transition = React.forwardRef(function Transition(props, ref) {
    return <Slide direction="up" ref={ref} {...props} />;
});

export function UiGridTable(props) {
    const classes = useSettingsStyles();
    const initState = {}
    for (const rowId in props.data) {
        for (const cellId in props.data[rowId]) {
            if (props.switches.includes(parseInt(cellId))) {
                const id = props.id + "-" + rowId + "-" + cellId;
                const data = props.data[rowId][cellId] instanceof Function ? props.data[rowId][cellId](rowId) : props.data[rowId][cellId];
                initState[id] = !!data;
            }
        }
    }
    const [state, setState] = useState(initState)

    const handleChange = (id) => {
        return (event, newValue) => {
            state[id] = newValue;
            setState(state);
        }
    };

    const [open, setOpen] = useState(false);
    const handleOpen = () => {
        setOpen(true);
    };

    const handleClose = () => {
        setOpen(false);
    };

    const headingRows = [];
    for (const heading of props.headings) {
        headingRows.push(<TableCell>{heading}</TableCell>)
    }


    const rows = []
    for (const rowId in props.data) {
        const children = [];
        for (const cellId in props.data[rowId]) {
            const id = props.id + "-" + rowId + "-" + cellId;
            const data = props.data[rowId][cellId] instanceof Function ? props.data[rowId][cellId](rowId) : props.data[rowId][cellId];
            if (props.switches.includes(parseInt(cellId))) {
                children.push(<TableCell><Switch checked={state[id]} onChange={handleChange(id)} id={id}/></TableCell>)
            } else {
                children.push(<TableCell>{data}</TableCell>)
            }
        }
        rows.push(<TableRow>{children}</TableRow>)
    }
    return (
        <Paper className={classes.paper}>
            <Typography variant="h6" component="div">
                <Grid container spacing={3}>
                    <Grid item xs={7}>
                        {props.title}
                    </Grid>
                    <Grid item xs={5}>
                        <ButtonGroup>
                            <Button onClick={handleOpen} startIcon={<Settings/>}>Change</Button>
                        </ButtonGroup>
                    </Grid>
                </Grid>
            </Typography>
            <Dialog
                fullScreen open={open} onClose={handleClose} TransitionComponent={Transition}
            >
            <AppBar position="static" className={classes.appBar}>
                <Toolbar>
                    <IconButton edge="start" color="inherit" onClick={handleClose} aria-label="close">
                        <Close/>
                    </IconButton>
                    <Typography variant="h6" className={classes.title}>
                        {props.title}
                    </Typography>
                    <HelpButton text={props.help} noFloat={true} title={props.label}/>
                </Toolbar>
            </AppBar>
                <TableContainer>
                    <Table stickyHeader className={classes.table} aria-label="simple table">
                        <TableHead>
                            <TableRow>
                                {headingRows}
                            </TableRow>
                        </TableHead>
                        <TableBody>
                            {rows}
                        </TableBody>
                    </Table>
                </TableContainer>
            </Dialog>
        </Paper>
    )
}