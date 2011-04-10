let SessionLoad = 1
if &cp | set nocp | endif
let s:cpo_save=&cpo
set cpo&vim
inoremap <Nul> 
imap <F3>  .i
map  :py EvaluateCurrentRange()
vmap 	 >gv
nmap 	 >>
omap 	 >>
noremap  :tabnew 
nmap gx <Plug>NetrwBrowseX
nnoremap <silent> <Plug>NetrwBrowseX :call netrw#NetrwBrowseX(expand("<cWORD>"),0)
nnoremap <silent> <F8> :TlistToggle
noremap <C-Right> gt
noremap <C-Left> gT
vmap <S-Tab> <gv
nmap <S-Tab> <<
omap <S-Tab> <<
map <F7> :! ctags-exuberant * modules/* 
map <F6> :s/\(^ *\)#/\1/ :let @/ = ""
map <F5> :s/\(^ *\)/\1#/ :let @/ = ""
map <F4> :wa :mksession!:xa
map <F2> : <Up>
map ù :silent nohl
abbr GPL_LICENSE ##################################################################################### copyright 2008 Gabriel Pettier <gabriel.pettier@gmail.com>## This file is part of PROJECT## PROJECT is free software: you can redistribute it and/or modify# it under the terms of the GNU General Public License as published by# the Free Software Foundation, either version 3 of the License, or# (at your option) any later version.## PROJECT is distributed in the hope that it will be useful,# but WITHOUT ANY WARRANTY; without even the implied warranty of# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the# GNU General Public License for more details.## You should have received a copy of the GNU General Public License# along with PROJECT.  If not, see <http://www.gnu.org/licenses/>.##################################################################################
let &cpo=s:cpo_save
unlet s:cpo_save
set autoindent
set autowrite
set background=dark
set backspace=indent,eol,start
set expandtab
set fileencodings=ucs-bom,utf-8,default,latin1
set helplang=fr
set history=50
set hlsearch
set incsearch
set listchars=tab:»·,trail:·
set nomodeline
set path=.,/usr/include,,,/usr/lib/python2.6,/usr/lib/python2.6/plat-linux2,/usr/lib/python2.6/lib-tk,/usr/lib/python2.6/lib-dynload,/usr/lib/python2.6/dist-packages,/usr/lib/python2.6/dist-packages/PIL,/usr/share/panda3d,/usr/lib64/panda3d,/usr/lib/python2.6/dist-packages/gst-0.10,/usr/lib/pymodules/python2.6,/usr/lib/python2.6/dist-packages/gtk-2.0,/usr/lib/pymodules/python2.6/gtk-2.0,/usr/lib/python2.6/dist-packages/wx-2.6-gtk2-unicode,/usr/lib/python2.6/dist-packages/wx-2.8-gtk2-unicode,/usr/local/lib/python2.6/dist-packages
set printoptions=paper:a4
set ruler
set runtimepath=~/.vim,/var/lib/vim/addons,/usr/share/vim/vimfiles,/usr/share/vim/vim72,/usr/share/vim/vimfiles/after,/var/lib/vim/addons/after,~/.vim/after
set scrolloff=2
set shiftwidth=4
set softtabstop=4
set suffixes=.bak,~,.swp,.o,.info,.aux,.log,.dvi,.bbl,.blg,.brf,.cb,.ind,.idx,.ilg,.inx,.out,.toc
set textwidth=79
set wildmenu
set window=47
let s:so_save = &so | let s:siso_save = &siso | set so=0 siso=0
let v:this_session=expand("<sfile>:p")
silent only
cd ~/usf/data/levels/tellera
if expand('%') == '' && !&modified && line('$') <= 1 && getline(1) == ''
  let s:wipebuf = bufnr('%')
endif
set shortmess=aoO
badd +0 tellara.xml
args tellara.xml
edit tellara.xml
set splitbelow splitright
set nosplitbelow
set nosplitright
wincmd t
set winheight=1 winwidth=1
argglobal
setlocal keymap=
setlocal noarabic
setlocal autoindent
setlocal nobinary
setlocal bufhidden=
setlocal buflisted
setlocal buftype=
setlocal nocindent
setlocal cinkeys=0{,0},0),:,0#,!^F,o,O,e
setlocal cinoptions=
setlocal cinwords=if,else,while,do,for,switch
setlocal comments=s1:/*,mb:*,ex:*/,://,b:#,:%,:XCOMM,n:>,fb:-
setlocal commentstring=/*%s*/
setlocal complete=.,w,b,u,t,i
setlocal completefunc=
setlocal nocopyindent
setlocal nocursorcolumn
setlocal nocursorline
setlocal define=
setlocal dictionary=
setlocal nodiff
setlocal equalprg=
setlocal errorformat=
setlocal expandtab
if &filetype != 'xml'
setlocal filetype=xml
endif
setlocal foldcolumn=0
setlocal foldenable
setlocal foldexpr=0
setlocal foldignore=#
setlocal foldlevel=0
setlocal foldmarker={{{,}}}
setlocal foldmethod=syntax
setlocal foldminlines=1
setlocal foldnestmax=20
setlocal foldtext=foldtext()
setlocal formatexpr=
setlocal formatoptions=tcq
setlocal formatlistpat=^\\s*\\d\\+[\\]:.)}\\t\ ]\\s*
setlocal grepprg=
setlocal iminsert=0
setlocal imsearch=0
setlocal include=
setlocal includeexpr=
setlocal indentexpr=
setlocal indentkeys=0{,0},:,0#,!^F,o,O,e
setlocal noinfercase
setlocal iskeyword=@,48-57,_,192-255
setlocal keywordprg=
setlocal nolinebreak
setlocal nolisp
set list
setlocal list
setlocal makeprg=
setlocal matchpairs=(:),{:},[:]
setlocal nomodeline
setlocal modifiable
setlocal nrformats=octal,hex
set number
setlocal number
setlocal numberwidth=4
setlocal omnifunc=
setlocal path=
setlocal nopreserveindent
setlocal nopreviewwindow
setlocal quoteescape=\\
setlocal noreadonly
setlocal norightleft
setlocal rightleftcmd=search
setlocal noscrollbind
setlocal shiftwidth=4
setlocal noshortname
setlocal nosmartindent
setlocal softtabstop=4
setlocal nospell
setlocal spellcapcheck=[.?!]\\_[\\])'\"\	\ ]\\+
setlocal spellfile=
setlocal spelllang=en
setlocal statusline=
setlocal suffixesadd=
setlocal swapfile
setlocal synmaxcol=3000
if &syntax != 'xml'
setlocal syntax=xml
endif
setlocal tabstop=8
setlocal tags=
setlocal textwidth=79
setlocal thesaurus=
setlocal nowinfixheight
setlocal nowinfixwidth
setlocal wrap
setlocal wrapmargin=0
2
normal zo
8
normal zo
11
normal zo
14
normal zo
17
normal zo
20
normal zo
23
normal zo
2
normal zo
let s:l = 24 - ((23 * winheight(0) + 23) / 47)
if s:l < 1 | let s:l = 1 | endif
exe s:l
normal! zt
24
normal! 025l
tabnext 1
if exists('s:wipebuf')
  silent exe 'bwipe ' . s:wipebuf
endif
unlet! s:wipebuf
set winheight=1 winwidth=20 shortmess=filnxtToO
let s:sx = expand("<sfile>:p:r")."x.vim"
if file_readable(s:sx)
  exe "source " . fnameescape(s:sx)
endif
let &so = s:so_save | let &siso = s:siso_save
doautoall SessionLoadPost
unlet SessionLoad
" vim: set ft=vim :
