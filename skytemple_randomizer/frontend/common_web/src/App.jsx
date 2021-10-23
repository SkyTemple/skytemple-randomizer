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
import CssBaseline from '@material-ui/core/CssBaseline';
import AppBar from "@material-ui/core/AppBar";
import Toolbar from "@material-ui/core/Toolbar";
import IconButton from "@material-ui/core/IconButton";
import {Info as InfoIcon, Shuffle} from "@material-ui/icons";
import Typography from "@material-ui/core/Typography";
import Tab from "@material-ui/core/Tab";
import SwipeableViews from "react-swipeable-views";
import TabContext from "@material-ui/lab/TabContext";
import {makeStyles} from "@material-ui/core/styles";
import useTheme from "@material-ui/core/styles/useTheme";
import TabPanel from "@material-ui/lab/TabPanel";
import Tabs from "@material-ui/core/Tabs";
import Fab from "@material-ui/core/Fab";
import Welcome from "./Welcome";
import Drawer from "@material-ui/core/Drawer";
import About from "./About";
import Settings from "./Settings";
import Dialog from "@material-ui/core/Dialog";
import {RandomizerPanel} from "./RandomizerPanel";

const useStyles = makeStyles((theme) => ({
    appbar: {
        backgroundColor: '#2f343f'
    },
    appbarTitle: {
        flexGrow: 1
    },
    fab: {
        position: 'fixed',
        bottom: theme.spacing(2),
        right: theme.spacing(2),
    },
    fullHeight: {
        minHeight: '100%'
    },
    topMargin: {
        marginTop: 104
    }
}));

function a11yProps(index) {
    return {
        id: `main-tab-${index}`,
        'aria-controls': `full-width-tabpanel-${index}`,
    };
}

export default function App() {
    const [activeTab, setActiveTab] = useState(0);
    const [aboutDrawer, setAboutDrawer] = useState(false);
    const [randomizeViewOpen, setRandomizeViewOpen] = useState(false);
    const classes = useStyles();
    const theme = useTheme();

    const handleChange = (event, newValue) => {
        setActiveTab(newValue);
        window.scrollTo(0, 0);
    };

    const toggleAboutDrawer = (open) => (event) => {
        if (event.type === 'keydown' && (event.key === 'Tab' || event.key === 'Shift')) {
            return;
        }
        setAboutDrawer(open);
    };

    const handleOpenRandomizeView = () => {
        setRandomizeViewOpen(true);
    };

    const handleCloseRandomizeView = () => {
        setRandomizeViewOpen(false);
    };

    return (
        <TabContext value={activeTab}>
            <CssBaseline/>
            <AppBar position="fixed" className={classes.appbar}>
                <Toolbar>
                    <Typography variant="h6" className={classes.appbarTitle}>
                        SkyTemple Randomizer
                    </Typography>
                    <IconButton color="inherit" aria-label="about" onClick={toggleAboutDrawer(true)}>
                        <InfoIcon/>
                    </IconButton>
                </Toolbar>
                <Tabs
                    value={activeTab}
                    onChange={handleChange}
                    indicatorColor="primary"
                    textColor="primary"
                    variant="scrollable"
                    scrollButtons="on"
                    aria-label="main tabs"
                >
                    <Tab label="Start" {...a11yProps(0)} />
                    <Tab label="Starters & More" {...a11yProps(1)} />
                    <Tab label="Dungeons" {...a11yProps(2)} />
                    <Tab label="Improvements" {...a11yProps(3)} />
                    <Tab label="P. Quiz" {...a11yProps(4)} />
                    <Tab label="Pokémon" {...a11yProps(5)} />
                    <Tab label="Locations" {...a11yProps(6)} />
                    <Tab label="Chapters" {...a11yProps(7)} />
                    <Tab label="Text" {...a11yProps(8)} />
                </Tabs>
            </AppBar>
            <SwipeableViews
                axis={theme.direction === 'rtl' ? 'x-reverse' : 'x'}
                index={activeTab}
                onChangeIndex={setActiveTab}
                className={classes.topMargin}
            >
                <TabPanel value={activeTab} index={0} dir={theme.direction}>
                    <Welcome/>
                </TabPanel>
                <TabPanel value={activeTab} index={1} dir={theme.direction}>
                    <Settings for="starters_npcs" />
                </TabPanel>
                <TabPanel value={activeTab} index={2} dir={theme.direction}>
                    <Settings for="dungeons" />
                </TabPanel>
                <TabPanel value={activeTab} index={3} dir={theme.direction}>
                    <Settings for="improvements" />
                </TabPanel>
                <TabPanel value={activeTab} index={4} dir={theme.direction}>
                    <Settings for="quiz" />
                </TabPanel>
                <TabPanel value={activeTab} index={5} dir={theme.direction}>
                    <Settings for="pokemon" />
                </TabPanel>
                <TabPanel value={activeTab} index={6} dir={theme.direction}>
                    <Settings for="locations" />
                </TabPanel>
                <TabPanel value={activeTab} index={7} dir={theme.direction}>
                    <Settings for="chapters" />
                </TabPanel>
                <TabPanel value={activeTab} index={8} dir={theme.direction}>
                    <Settings for="text" />
                </TabPanel>
            </SwipeableViews>
            <Fab color="primary" className={classes.fab} onClick={handleOpenRandomizeView}>
                <Shuffle/>
            </Fab>
            <RandomizerPanel open={randomizeViewOpen} onClose={handleCloseRandomizeView}/>
            <Drawer anchor='right' open={aboutDrawer} onClose={toggleAboutDrawer(false)}>
                <About onClose={toggleAboutDrawer(false)}/>
            </Drawer>
        </TabContext>
    );
}
