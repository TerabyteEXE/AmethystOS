if status is-interactive
    # Commands to run in interactive sessions can go here
    #
    set fish_greeting
end

if type -q starship
    starship init fish | source
end
