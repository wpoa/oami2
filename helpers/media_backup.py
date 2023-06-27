import subprocess
import progressbar

from sys import exit, stderr

class Media():
    def __init__(self, filename):
        self.filename = filename
        self.has_audio = False
        self.has_video = False
        self.position = 0
        self.lastposition = 0

    def find_streams(self):
        """
        Determines if media file has audio and / or video streams.
        """
        # TODO: Implement logic to check audio and video streams using ffmpeg
        pass

    def convert(self, outfile):
        """
        Converts media file to Ogg Theora or Ogg Theora+Vorbis using ffmpeg.
        """
        command = ['ffmpeg', '-i', self.filename, '-y', outfile]
        
        if self.has_video and self.has_audio:
            command.extend(['-c:v', 'libtheora', '-c:a', 'libvorbis'])
        elif self.has_video and not self.has_audio:
            command.extend(['-c:v', 'libtheora'])
        elif not self.has_video and self.has_audio:
            command.extend(['-c:a', 'libvorbis'])
        else:
            raise RuntimeError('Unknown audio/video stream combination.')

        process = subprocess.Popen(command, stderr=subprocess.PIPE)
        duration = None
        progress = None

        for line in process.stderr:
            line = line.decode().strip()
            if line.startswith('Duration:'):
                duration = self._parse_duration(line)
                progress = progressbar.ProgressBar(maxval=duration).start()
            elif line.startswith('frame='):
                position = self._parse_position(line)
                if duration is not None and progress is not None:
                    progress.update(position)
        
        if progress is not None:
            progress.finish()
        
        process.wait()

        if process.returncode != 0:
            print('ERROR: Conversion failed.\n')
            exit(1)

    def _parse_duration(self, line):
        duration_str = line.split(',')[0].split(':')[1].strip()
        hours, minutes, seconds = duration_str.split(':')
        duration = int(hours) * 3600 + int(minutes) * 60 + float(seconds)
        return duration

    def _parse_position(self, line):
        position_str = line.split('=')[1].split()[0].strip()
        hours, minutes, seconds = position_str.split(':')
        position = int(hours) * 3600 + int(minutes) * 60 + float(seconds)
        return position
