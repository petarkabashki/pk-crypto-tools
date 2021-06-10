function window_slider(len; subs=1)
    log2len = Int(trunc(log2(len)))
    
    start_slider_box = Observable{Any}(dom"div"())
    
    log2_slider = slider(1:log2len, label = "2^n els/wnd", default = log2len/2)
#     log2_slider

    window_size = Interact.@map (2 ^ &log2_slider)
    window_start = Observable{Int64}(1)
#     window_end = Observable{Int64}()
    window_end = Interact.@map min(len, (&window_start) + &window_size -1)
    
#     map!((wst,wsz) -> min(len, (wst + 1) * wsz  -1), window_end, window_start, window_size)
    
    function make_startslider(wnd_size) 
        window_start[] = 1
#         window_end[] = min(len, wnd_size)
        window_start_slider = slider(1:Int(trunc(len/wnd_size*subs)); label="window#", default=1)
        window_start_slider[] = 1
        
        map!((wst) -> Int64(trunc((wst-1)*wnd_size/subs)+1) , window_start, window_start_slider)
#         map!(wst -> min(len, (wst + 1) * wnd_size  -1) , window_end, window_start_slider)
        dom"div"(window_start_slider)
    end
    
    map!(make_startslider, start_slider_box, window_size)
#     output = Interact.@map (&window_no * &window_size , (1 + &window_no) * &window_size - 1)
    output = Interact.@map [&window_start , &window_end]
    
    wdg = Widget(["log2_slider" => log2_slider, "start_slider_box" => start_slider_box, "window_start" => window_start,
            "window_size" => window_size, "window_end" => window_end], output = output)
    @layout! wdg vbox(:start_slider_box, :log2_slider) ## custom layout: by default things are stacked vertically
end

function calc_wavelet(ar, m, wt)
#     wt = wavelet(wvlet)
    xt = dwt(ar, wt)
    threshold!(xt, BiggestTH(), m)
    fxt = idwt(xt, wt)
end
