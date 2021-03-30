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


import Typography from "@material-ui/core/Typography";
import Dialog from "@material-ui/core/Dialog";
import AppBar from "@material-ui/core/AppBar";
import Toolbar from "@material-ui/core/Toolbar";
import IconButton from "@material-ui/core/IconButton";
import {CheckCircle, ChevronRight, Close, GetApp, Warning} from "@material-ui/icons";
import React, {Fragment, useState} from "react";
import {makeStyles} from "@material-ui/core/styles";
import Slide from "@material-ui/core/Slide";
import Container from "@material-ui/core/Container";
import Box from "@material-ui/core/Box";
import Card from "@material-ui/core/Card";
import CardContent from "@material-ui/core/CardContent";
import Button from "@material-ui/core/Button";
import {Grid} from "@material-ui/core";
import Collapse from "@material-ui/core/Collapse";
import TextField from "@material-ui/core/TextField";
import LinearProgress from "@material-ui/core/LinearProgress";
import {ID_PREFIX, updateInConfig} from "./config";
import {UiTextField} from "./UiTextField";

// TO BE IMPLEMENTED BY CLIENT SIDE LOGIC:

/**
 * Callback response object
 * @typedef {Object} RandomizationEventContent
 * @property {?number} step - If type is PROGRESS: Current step number.
 * @property {?number} totalSteps - If type is PROGRESS: Total step number.
 * @property {?string} message - If type is ERROR: Error message / If type is PROGRESS: Current progress string.
 */

/**
 * Type of the event update
 * @readonly
 * @enum {number}
 */
window.RandomizationEventType = {
    PROGRESS: 1,
    DONE: 2,
    ERROR: 3
};

/**
 * Callback for the process reports.
 *
 * @callback processCallback
 * @param {RandomizationEventType} eventType
 * @param {RandomizationEventContent} content
 * @param {string} seed
 */

if (window.startRandomization === undefined) {
    /**
     * Starts the randomization process and runs it.
     * @param {File} file
     * @param {processCallback} processCallback
     * @param {object} config - See config python module: RandomizerConfig
     */
    window.startRandomization = function(file, processCallback, config) {
        throw Error("Randomization function not implemented.");
    };
}


// END - TO BE IMPLEMENTED BY CLIENT SIDE LOGIC

const RandomizationState = {
    UPLOAD: 0,
    RUNNING: 1,
    DONE_ERROR: 2
}

const useStyles = makeStyles((theme) => ({
    appbar: {
        backgroundColor: '#2f343f'
    },
    statusTitle: {
        fontSize: 14,
        marginRight: theme.spacing(1)
    },
    dialogPaper: {
        backgroundColor: '#383c4a'
    },
    grid: {
        marginTop: theme.spacing(2)
    },
    duskako: {
        maxWidth: "80%",
        display: "block",
        margin: "0 auto"
    },
    center: {
        textAlign: "center"
    },
    strike: {
        textDecoration: "line-through"
    }
}));

const Transition = React.forwardRef(function Transition(props, ref) {
    return <Slide direction="up" ref={ref} {...props} />;
});

function StatusPane(props) {
    const collapsed = props.actionId !== props.currentAction;

    const classes = useStyles();
    let collapsedClasses = classes.statusTitle + ' ';
    let icon = "";
    if (props.currentAction < props.actionId) {
        icon = <ChevronRight className={classes.statusTitle}/>
    } else if (props.currentAction > props.actionId) {
        collapsedClasses += classes.strike
        if (props.error) {
            icon = <Warning className={classes.statusTitle}/>
        } else {
            icon = <CheckCircle className={classes.statusTitle}/>
        }
    }
    return (
        <Card>
            <CardContent>
                <Collapse in={collapsed} mountOnEnter unmountOnExit>
                    {/** TITLE WHEN COLLAPSED **/}
                    <Typography className={collapsedClasses} color="textSecondary" gutterBottom>
                        <Grid container direction="row" alignItems="center">
                            <Grid item>
                                {icon}
                            </Grid>
                            <Grid item>
                                {props.title}
                            </Grid>
                        </Grid>
                    </Typography>
                </Collapse>
                {/** TITLE WHEN NOT COLLAPSED **/}
                <Collapse in={!collapsed} mountOnEnter unmountOnExit>
                    <Box>
                        <Typography variant="h5" component="h2">
                            {props.title}
                        </Typography>
                        {/** CONTENT WHEN NOT COLLAPSED **/}
                        <Typography variant="body2">
                            {props.children}
                        </Typography>
                    </Box>
                </Collapse>
            </CardContent>
        </Card>
    );
}

function LinearProgressWithLabel(props) {
  return (
    <Box display="flex" alignItems="center">
      <Box width="100%" mr={1}>
        <LinearProgress variant="determinate" {...props} />
      </Box>
      <Box minWidth={35}>
        <Typography variant="body2" color="textSecondary">{`${Math.round(
          props.value,
        )}%`}</Typography>
      </Box>
    </Box>
  );
}

export function RandomizerPanel(props) {
    const classes = useStyles();
    const [randomizingState, setRandomizingState] = useState(RandomizationState.UPLOAD);
    const [seed, setSeed] = useState("");
    /** @type {RandomizationEventContent} */
    const initOptions = {step: 0, totalSteps: 1, message: "Randomization is starting...\nThis may take a short while!"};
    const [runningState, setRunningState] = useState(initOptions);
    const [duskakoFeeling, setDuskakoFeeling] = useState("neutral");

    /**
      * Callback for the process reports.
      *
      * @type {processCallback}
      * @param {RandomizationEventType} eventType
      * @param {RandomizationEventContent} content
      * @param {string} seed
      */
    const processCallback = (eventType, content, seed) => {
        switch (eventType) {
            case RandomizationEventType.PROGRESS:
                setRunningState(content);
                setSeed(seed);
                break;
            case RandomizationEventType.DONE:
                setRandomizingState(RandomizationState.DONE_ERROR);
                setDuskakoFeeling("happy");
                break;
            case RandomizationEventType.ERROR:
                setRandomizingState(RandomizationState.DONE_ERROR);
                setRunningState(content);
                setDuskakoFeeling("sad");
                break;
        }
    };

    function processFiles(file) {
        setRandomizingState(RandomizationState.RUNNING);
        try {
            window.startRandomization(file, processCallback, window.loadedConfig);
        } catch (err) {
            processCallback(RandomizationEventType.ERROR, {message: "Unexpected client error: " + err.toString()}, "???");
        }
    }

    function onClose() {
        props.onClose();
        setRandomizingState(RandomizationState.UPLOAD);
        setSeed("");
        setRunningState(initOptions);
        setDuskakoFeeling("neutral");
    }

    return (
        <Dialog
            fullScreen open={props.open} onClose={() => false} TransitionComponent={Transition}
            PaperProps={{className: classes.dialogPaper}}
        >
            <AppBar position="static" className={classes.appbar}>
                <Toolbar>
                    <IconButton edge="start" color="inherit" onClick={onClose} aria-label="close"
                                disabled={randomizingState === RandomizationState.RUNNING}>
                        <Close/>
                    </IconButton>
                    <Typography variant="h6">
                        SkyTemple Randomizer
                    </Typography>
                </Toolbar>
            </AppBar>
            <Container maxWidth="sm">
                <Grid container spacing={3} className={classes.grid}>
                    <Grid item xs={12}>
                        <img src={"/data/duskako_" + duskakoFeeling + ".png"} className={classes.duskako}/>
                    </Grid>
                    <Grid item xs={12}>
                        <StatusPane title="1. Choose your ROM" actionId={RandomizationState.UPLOAD} currentAction={randomizingState} error={false}>
                            <p>You need a legally obtained ROM of the NA or EU version of the game.
                                Press the button below, to browse for a ROM file.
                                This will start the randomization process.</p>
                            <p>Note! Your device may freeze for a short while after selecting the ROM. Please stand by!</p>
                            <p>
                                <TextField
                                    id={ID_PREFIX + 'seed'} label="Seed" placeholder="(Automatic)"
                                    InputLabelProps={{shrink: true}}
                                    onChange={(event) => updateInConfig(ID_PREFIX + 'seed', event.target.value)}
                                />
                            </p>
                            <p>
                                <label htmlFor="main-rom">
                                    <input
                                        style={{display: 'none'}}
                                        id="main-rom"
                                        type="file"
                                        onChange={e => {
                                          processFiles(e.target.files[0]);
                                        }}
                                    />

                                    <Button color="secondary" variant="contained" component="span">
                                        Choose ROM & Start
                                    </Button>
                                </label>
                            </p>
                        </StatusPane>
                    </Grid>
                    <Grid item xs={12}>
                        <StatusPane title="2. Randomization" actionId={RandomizationState.RUNNING} currentAction={randomizingState} error={duskakoFeeling === "sad"}>
                            <Box className={classes.center}>
                                <Grid container spacing={1}>
                                    <Grid item xs={12}>
                                        <LinearProgressWithLabel value={runningState.step / runningState.totalSteps * 100} />
                                    </Grid>
                                    <Grid item xs={12}>
                                        <p>{runningState.message}</p>
                                        <Typography variant="subtitle1" component="p">
                                            {seed ? 'Your Seed: ' + seed : ''}
                                        </Typography>
                                    </Grid>
                                </Grid>
                            </Box>
                        </StatusPane>
                    </Grid>
                    <Grid item xs={12}>
                        <StatusPane title={duskakoFeeling === "sad" ? "Error!" : "3. Done!"} actionId={RandomizationState.DONE_ERROR} currentAction={randomizingState} error={false}>
                            {duskakoFeeling === "sad" ? (
                                <p>
                                    There was an error. Sorry! These are the details we got:<br />
                                    {runningState.message}
                                </p>
                            ) : (
                                <Fragment>
                                    <p>
                                        The randomization was successful! You can save the ROM now. It will show up
                                        in your downloads folder.
                                    </p>
                                    <p>
                                        <Button startIcon={<GetApp />} color="primary" variant="contained" href="/download">
                                            Save randomized ROM
                                        </Button>
                                    </p>
                                </Fragment>
                            )}
                        </StatusPane>
                    </Grid>
                </Grid>
            </Container>
        </Dialog>
    );
}