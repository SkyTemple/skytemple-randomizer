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
import {Close} from "@material-ui/icons";
import React, {useState} from "react";
import {makeStyles} from "@material-ui/core/styles";
import Slide from "@material-ui/core/Slide";
import Container from "@material-ui/core/Container";
import Box from "@material-ui/core/Box";
import Card from "@material-ui/core/Card";
import CardContent from "@material-ui/core/CardContent";
import CardActions from "@material-ui/core/CardActions";
import Button from "@material-ui/core/Button";
import {Grid} from "@material-ui/core";

const useStyles = makeStyles((theme) => ({
    appbar: {
        backgroundColor: '#2f343f'
    },
    statusTitle: {
        fontSize: 14,
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
    }
}));

const Transition = React.forwardRef(function Transition(props, ref) {
    return <Slide direction="up" ref={ref} {...props} />;
});

function StatusPane(props) {
    const classes = useStyles();
    return (
        <Card>
            <CardContent>
                <Slide direction="up" in={props.collapsed} mountOnEnter unmountOnExit>
                    {/** TITLE WHEN COLLAPSED **/}
                    <Typography className={classes.statusTitle} color="textSecondary" gutterBottom>
                        {props.title}
                    </Typography>
                </Slide>
                {/** TITLE WHEN NOT COLLAPSED **/}
                <Slide direction="up" in={!props.collapsed} mountOnEnter unmountOnExit>
                    <Box>
                        <Typography variant="h5" component="h2">
                            {props.title}
                        </Typography>
                        {/** CONTENT WHEN NOT COLLAPSED **/}
                        <Typography variant="body2">
                            {props.children}
                        </Typography>
                    </Box>
                </Slide>
            </CardContent>
        </Card>
    );
}

export function RandomizerPanel(props) {
    const classes = useStyles();
    // 0 -> upload ROM
    // 1 -> run
    // 2 -> done / error
    const [randomizingState, setRandomizingState] = useState(0);
    const duskakoFeeling = "neutral";

    function processFiles(file) {
        // lastModified: ...
        // lastModifiedDate: ...
        // name: ...
        // size: ...
        // type: ...
        // webkitRelativePath: ...
        alert(file.name);
        alert(file.size);
        alert(file.type);
    }

    return (
        <Dialog
            fullScreen open={props.open} onClose={() => false} TransitionComponent={Transition}
            PaperProps={{className: classes.dialogPaper}}
        >
            <AppBar position="static" className={classes.appbar}>
                <Toolbar>
                    <IconButton edge="start" color="inherit" onClick={props.onClose} aria-label="close"
                                disabled={randomizingState === 1}>
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
                        <StatusPane title="1. Choose your ROM" collapsed={false}>
                            <p>You need a legally obtained ROM of the NA or EU version of the game.
                                Press the button below, to browse for a ROM file.
                                This will start the randomization process.</p>
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
                        <StatusPane title="2. Randomization" collapsed={false}>
                            <Box className={classes.center}>
                                <p>Hello Content 2.</p>
                            </Box>
                        </StatusPane>
                    </Grid>
                    <Grid item xs={12}>
                        <StatusPane title="3. Done!" collapsed={false}>
                            <p>
                                The randomization was successful. Button.
                            </p>
                            <p>
                                There was an error. Whoopsie.
                            </p>
                        </StatusPane>
                    </Grid>
                </Grid>
            </Container>
        </Dialog>
    );
}