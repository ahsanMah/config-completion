package com.vmware.antlr4c3;

import java.io.File;
import java.io.IOException;
import java.util.*;

import org.antlr.v4.runtime.CharStreams;
import org.antlr.v4.runtime.CommonTokenStream;
import org.antlr.v4.runtime.ParserRuleContext;
import org.antlr.v4.runtime.Token;
import org.antlr.v4.runtime.TokenStream;
import org.antlr.v4.runtime.Vocabulary;
import org.antlr.v4.runtime.atn.ATN;
import org.antlr.v4.runtime.atn.ATNState;
import org.antlr.v4.runtime.atn.PredictionMode;
import org.antlr.v4.runtime.atn.Transition;
import org.antlr.v4.runtime.tree.ParseTree;
import org.antlr.v4.runtime.tree.TerminalNodeImpl;
import org.batfish.common.BatfishLogger;
import org.batfish.common.Warnings;
import org.batfish.config.Settings;
import org.batfish.config.Settings.TestrigSettings;
import org.batfish.datamodel.ConfigurationFormat;
import org.batfish.grammar.cisco.CiscoCombinedParser;
import org.batfish.grammar.cisco.CiscoLexer;
import org.batfish.grammar.cisco.CiscoParser;
import org.batfish.grammar.cisco.CiscoParser.Cisco_configurationContext;
import org.omg.PortableInterceptor.SYSTEM_EXCEPTION;
import org.apache.commons.io.FileUtils;

public class Driver {

    private static HashMap<Token, ParserRuleContext> contextMap = new HashMap<>();

    public static void main (String[] args) {
        String expression =
                "!\n" +
                "version 12.4\n" +
                "!\n" +
                "hostname B\n" +
                "!\n" +
                "access-list 1 deny 12.0.0.0 0.255.255.255\n" +
                "access-list 1 permit any\n"
//                "!\n" +
//                "interface GigabitEthernet0/1\n" +
//                "    description INFRA:C:Gi0/1\n" +
//                "    ip address 1.0.1.1 255.255.0.0\n" +
//                "    ip ospf cost 1\n" +
//                "    ip access-group 1 in\n" +
//                "!\n" +
//                "interface GigabitEthernet0/2\n" +
//                "    description INFRA:D:Gi0/1\n" +
//                "    ip address 3.0.1.2 255.255.0.0\n" +
//                "    ip ospf cost 1\n" +
//                "    ip access-group 1 in\n" +
//                "!\n" +
//                "interface GigabitEthernet0/3\n" +
//                "    ip address 11.0.1.3 255.0.0.0\n" +
//                "!\n" +
//                "router ospf 1\n" +
//                "    redistribute connected\n" +
//                "    network 3.0.0.0 0.0.255.255 area 0\n" +
//                "    network 1.0.0.0 0.0.255.255 area 0\n" +
//                "!\n" +
//                "end\n"
                ;

        args[0] = "/Users/ahsanmah/cs_projects/example_dump/single-ospf.txt";
        String ngramfile = "/Users/ahsanmah/cs_projects/config-completion/ngram_dump.csv";
        String ngramtext = "";

        File configuration = new File(args[0]);
        try {
            expression = FileUtils.readFileToString(configuration);
            ngramtext = FileUtils.readFileToString(new File(ngramfile));
        } catch (IOException e) {
            e.printStackTrace();
        }

        //Build map of prefixes to token predictions
        HashMap<String, List<String>> ngramMap = buildNgramMap(ngramtext);


		// Prepare batfish settings
		Settings batfishSettings = new Settings();
		batfishSettings.setLogger(new BatfishLogger(
				batfishSettings.getLogLevel(),
				batfishSettings.getTimestamp(), System.out));
		TestrigSettings batfishTestrigSettings = new TestrigSettings();
		batfishTestrigSettings.setBasePath(null); // FIXME?
		batfishSettings.setActiveTestrigSettings(batfishTestrigSettings);
		batfishSettings.setDisableUnrecognized(true);

		CiscoCombinedParser combined = new CiscoCombinedParser(expression,
                    batfishSettings, ConfigurationFormat.CISCO_IOS);

		CiscoLexer lexer = combined.getLexer();
		CiscoParser parser = combined.getParser();

        // Get all tokens
        TokenStream tokenStream  = parser.getInputStream();
        tokenStream.seek(0);
        List<Token> tokens = new LinkedList<>();
        int offset = 1;
        Token tok = tokenStream.LT(offset++);
        while (tok.getType() != Token.EOF) {
            tokens.add(tok);
            tok = tokenStream.LT(offset++);
//            break;
        }
        lexer.reset();

        // Specify our entry point
        lexer.removeErrorListeners();
        parser.removeErrorListeners();
        ParserRuleContext root = parser.cisco_configuration();

        CodeCompletionCore core = new CodeCompletionCore(parser, null, null);

        // 1) At the input start.

        Vocabulary vocabulary = parser.getVocabulary();

        //Parsing the tree to get tokens and their respective contexes
        collectCandidates(root, "");

        System.out.println("Line," + "Token Name," + "Candidates");

        for(int i = 1; i < tokens.size(); i++ ){

            Token prev_token = tokens.get(i-1);
            Token token = tokens.get(i);
            String prefix = prev_token.getText()+token.getText();

            //TODO: Clean up prefixes

//            System.out.println(prefix);
//            System.out.println(ngramMap.get(prefix));
//
//            System.out.print(token.getLine() + "," + token.getText() + ",");
            CodeCompletionCore.CandidatesCollection candidates =
                    core.collectCandidates(token.getTokenIndex()+1,contextMap.get(token));
//            System.out.println(candidates );

            List<String> tokenCandidates = new LinkedList<String>();
            for (Integer candidate : candidates.tokens.keySet()) {
                tokenCandidates.add(vocabulary.getDisplayName(candidate));
            }
//            Collections.sort(tokenCandidates);
//            System.out.println(tokenCandidates);

        }

        // TODO: For every token in the line, check to see if present in ngram map
        // Make histogram/bin counts of tokens that appear in tab completion

    }


    //Builds an association map from prefixes to a list of token predictions
    private static HashMap<String,List<String>> buildNgramMap(String ngramtext) {
        String[] mappings = ngramtext.split("\\n");
        String prefix;
        HashMap<String, List<String>> ngramMap = new HashMap<>();

        for (String line : mappings){
            String[] line_split = line.split(",");

            prefix = line_split[0]+line_split[1];
            List<String> predictions = new ArrayList<String>();

            for(int i=2; i < line_split.length; i++){
                String token = line_split[i];
                predictions.add(token);
//                System.out.println(predictions.get(i-2));
            }

            ngramMap.put(prefix,predictions);

        }

        return ngramMap;
    }

    private static void collectCandidates(ParserRuleContext context, String indent) {
        if (context.getChildCount() > 0) {
//            System.out.println(indent + context.getRuleIndex());

            int terminalChildren = 0;
            for (int i = 0; i < context.getChildCount(); i++) {
                ParseTree childTree = context.getChild(i);
                if (childTree instanceof ParserRuleContext) {
                    ParserRuleContext childContext = 
                            (ParserRuleContext)childTree;
                    collectCandidates(childContext, indent + "  ");
                } else if (childTree instanceof TerminalNodeImpl) {
                    terminalChildren++;
                }
            }

            if (terminalChildren > 0) {
                Token startToken = context.getStart();
                Token stopToken = context.getStop();
                contextMap.put(startToken, context);
//                System.out.println(indent + "BASE\t" + context + "\t" + startToken + "\t" + stopToken);
            }
        }
    }
}
