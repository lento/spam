## SPAM Spark Project & Asset Manager
##
## This program is free software; you can redistribute it and/or
## modify it under the terms of the GNU Lesser General Public
## License as published by the Free Software Foundation; either
## version 3 of the License, or (at your option) any later version.
##
## This program is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
## Lesser General Public License for more details.
##
## You should have received a copy of the GNU Lesser General Public
## License along with this program; if not, write to the
## Free Software Foundation, Inc., 59 Temple Place - Suite 330,
## Boston, MA 02111-1307, USA.
##
## Original Copyright (c) 2010, Lorenzo Pierfederici <lpierfederici@gmail.com>
## Contributor(s): 
##

<%inherit file="spam.templates.master"/>

<div id="loginform">
<form action="${tg.url('/login_handler')}" method="POST" class="loginfields">
    <h2><span>Login</span></h2>
    <input type="hidden" id="came_from" name="came_from" value="${came_from.encode('utf-8')}"></input>
    <input type="hidden" id="logins" name="__logins" value="${login_counter.encode('utf-8')}"></input>
    <label for="login">Username:</label><input type="text" id="login" name="login" class="text"></input>
    <label for="password">Password:</label><input type="password" id="password" name="password" class="text"></input>
    <input type="submit" id="submit" value="Login" />
</form>
</div>

