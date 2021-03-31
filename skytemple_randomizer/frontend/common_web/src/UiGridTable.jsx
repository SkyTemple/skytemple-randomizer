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
import {Close, ExpandLess, ExpandMore, Settings} from "@material-ui/icons";
import Button from "@material-ui/core/Button";
import Dialog from "@material-ui/core/Dialog";
import Slide from "@material-ui/core/Slide";
import AppBar from "@material-ui/core/AppBar";
import Grid from "@material-ui/core/Grid";
import Collapse from "@material-ui/core/Collapse";
import ListItemText from "@material-ui/core/ListItemText";
import ListItem from "@material-ui/core/ListItem";
import List from "@material-ui/core/List";
import TextField from "@material-ui/core/TextField";

const Transition = React.forwardRef(function Transition(props, ref) {
    return <Slide direction="up" ref={ref} {...props} />;
});

const CHUNK_SIZE = 20;

function SubTable(props) {
    const classes = useSettingsStyles();
    
    const rows = []
    for (const rowId in props.rows) {
        const children = [];
        for (const cellId in props.rows[rowId]) {
            const id = props.pid + "-" + rowId + "-" + cellId;
            const data = props.rows[rowId][cellId] instanceof Function ? props.rows[rowId][cellId](rowId) : props.rows[rowId][cellId];
            if (props.switches.includes(parseInt(cellId))) {
                children.push(<TableCell><Switch checked={props.states[id].val} onChange={props.handleChange(id)}
                                                 id={id}/></TableCell>)
            } else {
                children.push(<TableCell>{data}</TableCell>)
            }
        }
        rows.push(<TableRow>{children}</TableRow>)
    }
    
    return (
        <TableContainer>
            <Table stickyHeader className={classes.table} aria-label="simple table">
                <TableHead>
                    <TableRow>
                        {props.headingRows}
                    </TableRow>
                </TableHead>
                <TableBody>
                    {rows}
                </TableBody>
            </Table>
        </TableContainer>
    );
}

function SubCard(props) {
    const [expanded, setExpanded] = React.useState(false);

    const handleExpandClick = () => {
        setExpanded(!expanded);
    };
    const keys = Object.keys(props.rows);
    let fname = props.rows[keys[0]][0];
    fname = fname instanceof Function ? fname(keys[0]) : fname;
    let lname = props.rows[keys[keys.length-1]][0];
    lname = lname instanceof Function ? lname(keys[keys.length-1]) : lname;
    return (
        <List component="div" disablePadding>
            <ListItem button onClick={handleExpandClick}>
                <ListItemText primary={"Change '" + fname + "' - '" + lname + "'"} />
                {expanded ? <ExpandLess/> : <ExpandMore/>}
            </ListItem>
            <Collapse in={expanded} timeout="auto" unmountOnExit>
                <List component="div" disablePadding>
                    <ListItem disableGutters={true}>
                        <SubTable headingRows={props.headingRows} rows={props.rows} handleChange={props.handleChange} states={props.states} pid={props.pid} switches={props.switches}/>
                    </ListItem>
                </List>
            </Collapse>
        </List>
    );
}

function cutObjectIntoChunks(object, size) {
    const values = Object.values(object);
    const final = [];
    let counter = 0;
    let portion = {};

    for (const key in object) {
      if (counter !== 0 && counter % size === 0) {
        final.push(portion);
        portion = {};
      }
      portion[key] = values[counter];
      counter++
    }
    final.push(portion);
    return final;
}

export function UiGridTable(props) {
    const classes = useSettingsStyles();
    const states = {}
    const mapping = {}
    for (const rowId in props.data) {
        for (const cellId in props.data[rowId]) {
            if (props.switches.includes(parseInt(cellId))) {
                const id = props.id + "-" + rowId + "-" + cellId;
                const data = props.data[rowId][cellId] instanceof Function ? props.data[rowId][cellId](rowId) : props.data[rowId][cellId];
                const [state, setState] = useState(data);
                states[id] = {val: state, set: setState};
                mapping[id] = {rowId, cellId};
            }
        }
    }

    const handleChange = (id) => {
        return (event, newValue) => {
            states[id].set(newValue);
            props.onChange(props.id, mapping[id].rowId, mapping[id].cellId, newValue);
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

    // For performance reasons, we group sets of CHUNK_SIZE rows.
    let dialogContent;
    if (Object.keys(props.data).length <= CHUNK_SIZE) {
        dialogContent = <SubTable headingRows={headingRows} rows={props.data} handleChange={handleChange} states={states} pid={props.id} switches={props.switches}/>;
    } else {
        dialogContent = [];
        for (const chunk of cutObjectIntoChunks(props.data, CHUNK_SIZE)) {
            dialogContent.push(<SubCard headingRows={headingRows} rows={chunk} handleChange={handleChange} states={states} pid={props.id} switches={props.switches}/>);
        }
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
                {dialogContent}
            </Dialog>
        </Paper>
    )
}