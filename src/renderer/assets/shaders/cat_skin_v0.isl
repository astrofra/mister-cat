surface {
  alpha-test : true,
  z-write: false
}

in {
	tex2D catskin_map [wrap-u: clamp, wrap-v: clamp];
	tex2D pattern_map [wrap-u: repeat, wrap-v: repeat];
	vec3 skin_color_0 [hint: color];
	vec3 skin_color_1 [hint: color];
	vec3 skin_color_2 [hint: color];		
	vec3 edges_color [hint: color];
	vec3 shiny_color [hint: color];
	float color_pattern_blend = 0.0;
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
			vec2 v_ssuv = %in.fragcoord%.xy * vInverseInternalResolution.xy;
			vec4 col = texture2D(catskin_map, v_uv);
			vec3 patt = texture2D(pattern_map, v_ssuv).xyz;
			vec3 body_color = skin_color_0 * patt.x + skin_color_1 * patt.y + skin_color_2 * patt.z;
			body_color = body_color * color_pattern_blend + (1.0 - color_pattern_blend) * ((skin_color_0 + skin_color_1) * 0.5);

			%diffuse% = vec3(0,0,0);
			%constant% = edges_color * col.x + body_color * col.y + shiny_color * col.z;
			%opacity% = col.w;
		%}
	}
}
