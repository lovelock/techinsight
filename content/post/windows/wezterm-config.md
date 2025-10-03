---
title: "Wezterm Config"
description: 
date: 2025-10-03T23:09:31+08:00
image: 
math: true
license: 
hidden: false
comments: true
categories: ["Windows"]
tags: ["wezterm", "terminal"]
---

Windows 11下的Windows Terminal堪堪一用，但在Windows 10 上官方的这些东西就完全没法用了，Wezterm还稍微有点定制性，花了点时间设置了一个自己需要的。

```lua
-- These are the basic's for using wezterm.
-- Mux is the mutliplexes for windows etc inside of the terminal
-- Action is to perform actions on the terminal
local wezterm = require 'wezterm'
local mux = wezterm.mux
local act = wezterm.action

-- These are vars to put things in later (i dont use em all yet)
local config = {}
local keys = {}
local mouse_bindings = {}
local launch_menu = {
    {
        label = 'PowerShell 7',
        domain = 'DefaultDomain',
        args = {'C:\\Program Files\\PowerShell\\7\\pwsh.exe'}
    },
    {
        label = 'WSL(Debian)',
        args = {'wsl', '-d', 'Debian'}
    },
    {
        label = 'Git Bash',
        domain = 'DefaultDomain',
        args = {'C:\\Program Files\\Git\\bin\\bash.exe'}
    }
}

-- This is for newer wezterm vertions to use the config builder 
if wezterm.config_builder then
    config = wezterm.config_builder()
end

-- Default config settings
-- These are the default config settins needed to use Wezterm
-- Just add this and return config and that's all the basics you need

-- Color scheme, Wezterm has 100s of them you can see here:
-- https://wezfurlong.org/wezterm/colorschemes/index.html
config.color_scheme = 'Oceanic Next (Gogh)'
-- This is my chosen font, we will get into installing fonts on windows later
config.font = wezterm.font('FiraCode Nerd Font')
config.font_size = 12
config.launch_menu = launch_menu
-- makes my cursor blink 
config.default_cursor_style = 'BlinkingBar'
config.disable_default_key_bindings = true
-- this adds the ability to use ctrl+v to paste the system clipboard 

config.keys = { -- Ctrl+V 粘贴
{
    key = 'V',
    mods = 'CTRL',
    action = act.PasteFrom 'Clipboard'
}, -- Ctrl+Shift+N 打开环境选择菜单
{
    key = 't',
    mods = 'CTRL',
    action = act.SpawnTab 'CurrentPaneDomain'
}, -- 新增一些常用快捷键
{
    key = 'c',
    mods = 'CTRL',
    action = act.CopyTo 'ClipboardAndPrimarySelection'
}, {
    key = 'n',
    mods = 'CTRL',
    action = act.SpawnWindow
}, {
    key = 'w',
    mods = 'CTRL',
    action = act.CloseCurrentTab {
        confirm = true
    }
}}
config.mouse_bindings = mouse_bindings

-- There are mouse binding to mimc Windows Terminal and let you copy
-- To copy just highlight something and right click. Simple
mouse_bindings = {{
    event = {
        Down = {
            streak = 3,
            button = 'Left'
        }
    },
    action = wezterm.action.SelectTextAtMouseCursor 'SemanticZone',
    mods = 'NONE'
}, {
    event = {
        Down = {
            streak = 1,
            button = "Right"
        }
    },
    mods = "NONE",
    action = wezterm.action_callback(function(window, pane)
        local has_selection = window:get_selection_text_for_pane(pane) ~= ""
        if has_selection then
            window:perform_action(act.CopyTo("ClipboardAndPrimarySelection"), pane)
            window:perform_action(act.ClearSelection, pane)
        else
            window:perform_action(act({
                PasteFrom = "Clipboard"
            }), pane)
        end
    end)
}}

-- This is used to make my foreground (text, etc) brighter than my background
config.foreground_text_hsb = {
    hue = 1.0,
    saturation = 1.2,
    brightness = 1.5
}

-- IMPORTANT: Sets WSL2 Debian as the defualt when opening Wezterm
-- config.default_domain = 'WSL:Debian'
config.default_domain = 'local'
-- 此处路径替换为你实际的 pwsh.exe 路径
config.default_prog = {"C:\\Program Files\\PowerShell\\7\\pwsh.exe"}

return config
```

这样可以对【+】右键呼出菜单，选择想要的Shell了。
