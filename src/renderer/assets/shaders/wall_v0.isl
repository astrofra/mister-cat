in {
	tex2D wall_map [wrap-u: clamp, wrap-v: clamp];
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
			%constant% = texture2D(wall_map, vec2(0.0,1.0) + (v_ssuv * vec2(1.0,-1.0))).xyz;
		%}
	}
}
