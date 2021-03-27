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

import {red} from '@material-ui/core/colors';
import {createMuiTheme, makeStyles} from '@material-ui/core/styles';

// A custom theme for this app
const theme = createMuiTheme({
    palette: {
        type: 'dark',
        primary: {
            main: '#5294e2',
        },
        secondary: {
            main: '#5294e2',
        },
        error: {
            main: red.A400,
        },
        surface: {
            default: '#404552'
        },
        background: {
            default: '#383c4a',
            paper: '#404552'
        },
    },
});

export default theme;

export const useSettingsStyles = makeStyles((theme) => ({
    appbar: {
        backgroundColor: '#2f343f'
    },
    paper: {
        padding: theme.spacing(2),
        position: "relative",
    },
    toolbar: {
        position: "relative",
    },
    helpButton: {
        position: "absolute",
        right: theme.spacing(2),
        top: "calc(50% - 16px)"
    },
    elem: {
        maxWidth: "85%"
    }
}));
