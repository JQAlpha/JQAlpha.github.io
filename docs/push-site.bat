@echo off
setlocal enabledelayedexpansion
chcp 65001 >nul
title github-pages - 发布脚本

echo ============================================================
echo   github-pages  ·  发布到 https://jqalpha.com
echo ============================================================
echo.

cd /d "%~dp0.."
set "PROJECT=%CD%"

echo [1/4] 检查仓库状态...
git rev-parse --is-inside-work-tree >nul 2>&1
if errorlevel 1 (
    echo      ERROR: 不是 git 仓库，请检查目录
    pause
    exit /b 1
)

git status --short | findstr /v "^$" >nul 2>&1
if errorlevel 1 (
    echo      工作区干净，无改动可发布
) else (
    echo.
    echo      待提交的改动：
    git status --short
)

echo.
echo [2/4] 本地构建校验...
call npm run build
if errorlevel 1 (
    echo.
    echo      构建失败，已中止。请先修复上述错误。
    pause
    exit /b 1
)

echo.
echo [3/4] 提交并推送...
if not "%~1"=="" (
    set "MSG=%~1"
) else (
    set "MSG=chore: 更新站点内容"
)

git add -A
git commit -m "!MSG!" 2>nul
if errorlevel 1 (
    echo      没有需要提交的改动，跳过 commit
)

git push origin main
if errorlevel 1 (
    echo.
    echo      推送失败。检查项：
    echo        - SSH 密钥是否可用：ssh -T git@github.com
    echo        - 网络是否能连通 github.com
    pause
    exit /b 1
)

echo.
echo [4/4] 等待 CI 部署...
echo      打开以下链接查看进度：
echo        https://github.com/JQAlpha/JQAlpha.github.io/actions
echo.
echo      通常 1-2 分钟完成，之后访问：
echo        https://jqalpha.com
echo.

pause
