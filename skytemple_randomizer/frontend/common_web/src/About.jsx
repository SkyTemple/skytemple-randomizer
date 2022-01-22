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
import React, {Fragment} from "react";
import Link from "@material-ui/core/Link";
import {IconButton} from "@material-ui/core";
import {Close} from "@material-ui/icons";
import ButtonGroup from "@material-ui/core/ButtonGroup";
import makeStyles from "@material-ui/core/styles/makeStyles";
import TableContainer from "@material-ui/core/TableContainer";
import Table from "@material-ui/core/Table";
import TableRow from "@material-ui/core/TableRow";
import TableCell from "@material-ui/core/TableCell";
import TableBody from "@material-ui/core/TableBody";
import Paper from "@material-ui/core/Paper";
import Container from "@material-ui/core/Container";

const useStyles = makeStyles((theme) => ({
    close: {
        position: "fixed",
        top: theme.spacing(1),
        right: theme.spacing(2)
    },
    logo: {
        width: "50%",
        display: "block",
        margin: "0 auto"
    },
    nameCell: {
        fontWeight: "bold"
    },
    noBorder: {
        border: "none"
    },
    about: {
        padding: theme.spacing(2)
    }
}));

const CREDITS = {
    "Project Lead:": [
        ["Marco \"Capypara\" Köpcke", "http://github.com/parakoopa"]
    ],
    "Contributors": [
        ["Aikku93 (via tilequant)", "http://github.com/aikku93"],
        ["techticks (MacOS packaging)", "https://github.com/tech-ticks"],
        ["marius851000 (via skytemple-rust)", "http://github.com/marius851000"]
    ],
    "Lead Hackers": [
        ["psy_commando", "http://github.com/psyCommando"],
        ["End45", "http://github.com/End45"]
    ],
    "Total Team Control Patch": [
        ["Cipnit", "https://www.pokecommunity.com/member.php?u=751556"]
    ],
    "Hackers": [
        ["evandixon", "http://github.com/evandixon"],
        ["MegaMinerd", null],
        ["Nerketur", null],
        ["UsernameFodder", "http://reddit.com/u/UsernameFodder"]
    ],
    "Documentation": [
        ["frostibirb", null],
        ["MaxSchersey", null]
    ],
    "Testing": [
        ["DiST (MAN-K)", null],
        ["Jester", null],
        ["KingPriceman", null],
        ["Maestroke", null],
        ["MandL27", null],
        ["NeroIntruder", null],
        ["Scyrous", null],
        ["yakkomon", null]
    ],
    "Artwork": [
        ["Charburst (Logo and Illustrations)", "https://twitter.com/Charburst_"],
        ["Aviivix (UI Icons)", "https://twitter.com/aviivix"],
        ["Edael (Duskako Sprites)", "https://twitter.com/Exodus_Drake"]
    ],
    "Special Thanks": [
        ["Audino", "https://github.com/audinowho"],
        ["Fireally", "https://www.youtube.com/channel/UCslMDS9pAH-ay6qqKlyyJzw"],
        ["Soniclink137", null],
        ["DasK", "https://www.reddit.com/user/thedask"],
        ["Apuapua", null],
        ["TheGoldCrow", "https://www.youtube.com/thegoldcrow"],
        ["DrGlutamate", null],
        ["ケLV", "https://clv.carrd.co"],
        ["Quilavabom", null],
        ["MrStrouder", null]
    ]
}

function getRows(classes) {
    const rows = [];
    for (const creditGroupName in CREDITS) {
        const creditGroup = CREDITS[creditGroupName];
        let first = true;
        let i = 0;
        for (const credit of creditGroup) {
            const last = i === creditGroup.length - 1;
            rows.push(
                <TableRow>
                    <TableCell align="right" className={last ? classes.nameCell : classes.nameCell + ' ' + classes.noBorder}>{first ? creditGroupName : ""}</TableCell>
                    <TableCell align="right" className={last ? '' : classes.noBorder}>
                        {credit[1] ? (
                            <Link href={credit[1]} target="_blank">{credit[0]}</Link>
                        ) : (
                            <Fragment>{credit[0]}</Fragment>
                        )}
                    </TableCell>
                </TableRow>
            );
            first = false;
            i++;
        }
    }
    return rows;
}

export default function About(props) {
    const classes = useStyles();
    return (
        <Paper elevation={0} className={classes.about}>
            <ButtonGroup className={classes.close}>
                <IconButton color="inherit" aria-label="close" onClick={props.onClose}>
                    <Close/>
                </IconButton>
            </ButtonGroup>
            <img src="/static/logo.png" className={classes.logo}/>
            <Typography variant="h4" align="center">
                <p>
                    SkyTemple Randomizer
                </p>
            </Typography>
            <Typography variant="body1" align="center">
                <p>
                    {VERSION}
                </p>
                <p>
                    Application to randomize the ROM of Pokémon Mystery Dungeon Explorers of Sky (EU/US).
                </p>
                <p>
                    <Link href="https://github.com/SkyTemple/skytemple-randomizer" target="_blank">
                        https://github.com/SkyTemple/skytemple-randomizer
                    </Link>
                </p>
                <p>
                    This program comes with absolutely no warranty.
                    See the <Link href="https://www.gnu.org/licenses/gpl-3.0.html" target="_blank">GNU General Public License, version 3
                    or later</Link> for details.
                </p>
            </Typography>
            <Paper variant="outlined">
                <Container>
                    <Typography variant="h5" align="center">
                        <p>
                            Credits
                        </p>
                    </Typography>
                    <TableContainer>
                        <Table size="small" className={classes.table}>
                            <TableBody>
                                {getRows(classes)}
                            </TableBody>
                        </Table>
                    </TableContainer>
                </Container>
            </Paper>
        </Paper>
    )
};
