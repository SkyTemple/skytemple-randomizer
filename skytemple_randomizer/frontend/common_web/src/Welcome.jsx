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
import React from "react";
import Container from "@material-ui/core/Container";
import Box from "@material-ui/core/Box";
import Link from "@material-ui/core/Link";
import {makeStyles} from "@material-ui/core/styles";

const useStyles = makeStyles((theme) => ({
    logo: {
        width: "50%",
        display: "block",
        margin: "0 auto"
    }
}));

export default function Welcome() {
    const classes = useStyles();
    return (
        <Container maxWidth="sm">
            <Box>
                <img src="/static/logo.png" className={classes.logo} />
                <Typography variant="h5" align="center">
                    <p>
                        Welcome to the SkyTemple Randomizer!
                    </p>
                </Typography>
                <Typography variant="body1" align="center">
                    <p>
                        Have fun creating a new and unique Explorers of Sky Experience!
                    </p>
                    <p>
                        Get started by clicking the play icon.<br/>
                        You can customize randomization settings in the other tabs.
                    </p>
                    <p>
                        Find out more about SkyTemple at&nbsp;
                        <Link href="https://skytemple.org/" target="_blank">
                            skytemple.org
                        </Link>.
                    </p>
                </Typography>
            </Box>
        </Container>
    )
};
