{
  pkgs ? import <nixpkgs> { },
}:

pkgs.mkShell {
  buildInputs = with pkgs; [
    python311
    ollama
    pandoc
    texliveSmall

    stdenv.cc.cc.lib
    zlib
    libffi
    openssl
  ];

  shellHook = ''
    export LD_LIBRARY_PATH="${pkgs.stdenv.cc.cc.lib}/lib:${pkgs.zlib}/lib:$LD_LIBRARY_PATH"
    if [ ! -d venv ]; then
        python -m venv venv
        venv/bin/pip install --upgrade pip
        venv/bin/pip install -q -r requirements-dev.txt
    fi
    source venv/bin/activate
  '';
}
