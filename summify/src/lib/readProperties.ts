// @ts-nocheck
import * as fs from 'fs';
import * as path from 'path';

export class PropertiesReader{
    private logger: Logger;

    constructor(kwargs?: any) {
        if (kwargs?.logger) {
        this.logger = kwargs.logger;
        } else {
        const loging = new Logger();
        this.logger = loging  //.getLogger();
        }
    }

    readProperties(filePath: string): { [key: string]: string } {
        const absolutePath = path.resolve(__dirname, filePath);
        try {
            const data = fs.readFileSync(absolutePath, 'utf8');
            const lines = data.split('\\n');
            const properties: { [key: string]: string } = {};

            for (const line of lines) {
                const trimmedLine = line.trim();
                if (trimmedLine && !trimmedLine.startsWith('#')) {
                    const [key, value] = trimmedLine.split('=').map(part => part.trim());
                    if (key && value) {
                        properties[key] = value;
                    }
                }
            }

            return properties;
        } catch (err) {
            console.error("Error reading properties file:", err);
            return {};
        }
    }
}