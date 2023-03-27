surface {
  blend : alpha,
  z-write : false
}

in {
	tex2D paint_map [wrap-u: clamp, wrap-v: clamp];
	tex2D alpha_map [wrap-u: clamp, wrap-v: clamp];
}

variant {
	vertex {
		out {
			vec2 v_uv;
		}

		source %{
			v_uv = vUV0;
		%}
	}

	pixel {
		source %{
			vec2 v_ssuv = %in.fragcoord%.xy * vInverseInternalResolution.xy; // * vec2(2.0, 1.25);
			%diffuse% = vec3(0,0,0);
			vec4 paint_col = texture2D(paint_map, vec2(0.0,1.0) + (v_uv * vec2(1.0,-1.0)));
			%constant% = paint_col.xyz;
			%opacity% = texture2D(alpha_map, vec2(0.0,1.0) + (v_ssuv * vec2(1.0,-1.0))).x * paint_col.w;
		%}
	}
}
